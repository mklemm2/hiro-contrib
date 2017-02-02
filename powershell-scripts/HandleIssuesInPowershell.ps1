######################################################################################
#                 workaround for quality software made in Redmond                    #
######################################################################################
$uriFixerDef = @'
using System;
using System.Reflection;

public class UriFixer
{
    private const int UnEscapeDotsAndSlashes = 0x2000000;
    private const int SimpleUserSyntax = 0x20000;

    public static void LeaveDotsAndSlashesEscaped(Uri uri)
    {
        if (uri == null)
            throw new ArgumentNullException("uri");

        FieldInfo fieldInfo = uri.GetType().GetField("m_Syntax", BindingFlags.Instance | BindingFlags.NonPublic);
        if (fieldInfo == null)
            throw new MissingFieldException("'m_Syntax' field not found");

        object uriParser = fieldInfo.GetValue(uri);
        fieldInfo = typeof(UriParser).GetField("m_Flags", BindingFlags.Instance | BindingFlags.NonPublic);
        if (fieldInfo == null)
            throw new MissingFieldException("'m_Flags' field not found");

        object uriSyntaxFlags = fieldInfo.GetValue(uriParser);

        // Clear the flag that we do not want
        uriSyntaxFlags = (int)uriSyntaxFlags & ~UnEscapeDotsAndSlashes;
        uriSyntaxFlags = (int)uriSyntaxFlags & ~SimpleUserSyntax;
        fieldInfo.SetValue(uriParser, uriSyntaxFlags);
    }
}
'@
Add-Type -TypeDefinition $uriFixerDef


######################################################################################
#                                      Functions                                     #
######################################################################################

# get API token
function GetAuth([String] $WSO2URL, [String] $ClientID, [String] $ClientSecret) {
  # allow Self-signed certs
  [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
  # REST call
  return Invoke-RestMethod -Method Post -Uri "$WSO2URL/oauth2/token" -ContentType "application/x-www-form-urlencoded;charset=UTF-8" -Body "grant_type=client_credentials&scope=batchjob&client_id=$ClientID&client_secret=$ClientSecret"
}

# create XML data for Issue
function CreateIssueData {
  [cmdletbinding()]
  Param (
    [parameter(ValueFromPipeline=$True)] [Object[]] $Variable,
    [String] $NodeID,
    [String] $IssueID,
    [String] $IssueSubject
  )

  Begin {
    Set-Variable -Name 'IssueSchema' -option Constant -value 'https://graphit.co/schemas/v2/IssueSchema'
    $IFR = [XML] "<Issue xmlns=""$IssueSchema"" />"

    if($NodeID) {
      $nodeidattr = $IFR.CreateAttribute("NodeID")
      $nodeidattr.set_Value($NodeID) | out-null
      $IFR.Issue.SetAttributeNode($nodeidattr) | out-null
    }
    if($IssueSubject) {
      $subjectattr = $IFR.CreateAttribute("IssueSubject")
      $subjectattr.set_Value($IssueSubject) | out-null
      $IFR.Issue.SetAttributeNode($subjectattr) | out-null
    }
    if($IssueID) {
      $iidattr = $IFR.CreateAttribute("IID")
      $iidattr.set_Value($IssueID) | out-null
      $IFR.Issue.SetAttributeNode($iidattr) | out-null
    }
  }

  Process {
    ForEach($var in $Variable) {
    $var.GetEnumerator() | % {
      $varNode = $IFR.CreateElement($_.key, $IssueSchema)
      $_.value | % {
        $contentNode = $IFR.CreateElement("Content", $IssueSchema)
        $varNode.AppendChild($contentNode) | out-null
        if($_ -is [string]) {
          $valAttr = $IFR.CreateAttribute("Value")
          $valAttr.set_Value($_) | out-null
          $contentNode.SetAttributeNode($valAttr) | out-null
        } elseif ($_ -is [Object]) {
          $_.GetEnumerator() | % {
            $valAttr = $IFR.CreateAttribute("Value")
            $valAttr.set_Value($_.value) | out-null
            $contentNode.SetAttributeNode($valAttr) | out-null
            $keyAttr = $IFR.CreateAttribute("Key")
            $keyAttr.set_Value($_.key) | out-null
            $contentNode.SetAttributeNode($keyAttr) | out-null
          }
        }
      

      }
      $IFR.Issue.AppendChild($varNode) | out-null
    }
    }
  }

  End {
    Write-Output $IFR
  }
}

# Do Unix/C-style escaping (only double quotes and backslash at this point)
filter Unix-Escape-String { 
    return ( ( $_ -replace '(\\*)\\','$1$1\\' ) -replace '(\\*)"','$1$1\"'  )
}

# create the JSON envelope for GraphIT
function CreateIssueJSON {
  [cmdletbinding()]
  Param(
    [parameter(ValueFromPipeline=$True)] [String] $IssueFormalRepresentation,
    [switch] $ResetDeploymentStatus
  )

  if(-Not $ResetDeploymentStatus) {
    $issuedata = @"
{
  "ogit/Automation/issueFormalRepresentation" : "$($IssueFormalRepresentation|Unix-Escape-String)"
}
"@
  } else {
    $issuedata = @"
{
  "ogit/Automation/issueFormalRepresentation" : "$($IssueFormalRepresentation|Unix-Escape-String)",
  "ogit/Automation/deployStatus": null,
  "ogit/Automation/isDeployed": null
}
"@
  }
  Write-Output $issuedata
}

# Put a new Issue in GraphIT
function PutIssue {
  [cmdletbinding()]
  Param(
    [parameter(Mandatory=$True,ValueFromPipeline=$True)] [Object] $XML,
    [parameter(Mandatory=$True)] [String] $GraphitURL,
    [parameter(Mandatory=$True)] [Object] $Auth
  )
  Set-Variable -Name 'IssueOgitType' -option Constant -value 'ogit%2FAutomation%2FAutomationIssue'
  $NodeID = $XML.Issue | select NodeID
  if($NodeID -notmatch '[a-zA-Z0-9\-+_.]+:[a-zA-Z0-9\-+_.]+:(Machine|Software|Resource|Application):[a-zA-Z0-9\-+_.]*') { Throw "NodeID missing or malformed!" }
  # build URI and fix .NET 4.5 issue where %2F is converted back to /
  $myuri = "$GraphitURL/new/$IssueOgitType"
  [UriFixer]::LeaveDotsAndSlashesEscaped($myuri)

  ## allow Self-signed certs
  [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
  
  # REST call
  $result = Invoke-RestMethod -Method Post -Uri $myuri -ContentType "application/json" -Body "$($XML.OuterXML| CreateIssueJSON)" -Headers @{_TOKEN=$Auth.access_token}

  while($result.'ogit/Automation/isDeployed' -ne 'true') {
    Start-Sleep -m 250
    $result = Invoke-RestMethod -Method Get -Uri "$GraphitURL/$($result.'ogit/_id')" -ContentType "application/json" -Headers @{_TOKEN=$Auth.access_token}
    if($i++ -gt 40) { Throw "Issue was not deployed!" }
  }
  Write-Output $result
}

# Update an existing Issue
function UpdateIssue {
  [cmdletbinding()]
  Param(
    [parameter(Mandatory=$True,ValueFromPipeline=$True)] [Object] $XML,
    [parameter(Mandatory=$True)] [String] $GraphitURL,
    [parameter(Mandatory=$True)] [Object] $Auth
  )
  $IssueID = ($XML.Issue | select IID).IID
  if($IssueID -notmatch '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}') { Throw "IssueID missing or malformed!" }
  $myuri = "$GraphitURL/$IssueID"
  [UriFixer]::LeaveDotsAndSlashesEscaped($myuri)

  ## allow Self-signed certs
  [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
  
  # REST call
  $result = Invoke-RestMethod -Method Post -Uri $myuri -ContentType "application/json" -Body "$($XML.OuterXML| CreateIssueJSON -ResetDeploymentStatus)" -Headers @{_TOKEN=$Auth.access_token}
  while($result.'ogit/Automation/isDeployed' -ne 'true') {
    Start-Sleep -m 250
    $result = Invoke-RestMethod -Method Get -Uri "$GraphitURL/$($result.'ogit/_id')" -ContentType "application/json" -Headers @{_TOKEN=$Auth.access_token}
    if($i++ -gt 40) { Throw "Issue was not deployed!" }
  }
    Write-Output $result
}

