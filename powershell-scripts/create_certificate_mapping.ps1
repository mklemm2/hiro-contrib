[CmdLetBinding()]
param
(
    [Parameter(Mandatory=$true)]
    [String] $Issuer,
	
    [Parameter(Mandatory=$true)]
    [String] $Subject,

	[Parameter(Mandatory=$true)]
	[String] $Username
)

$Logfile = "c:\windows\logs\create_certificate_mapping.log"

Function log
{
	Param ([string]$logstring)

	$nowDate = Get-Date -format dd.MM.yyyy
    $nowTime = Get-Date -format HH:mm:ss
	write-verbose -message $logstring
	Add-content $Logfile -value "[$nowDate][$nowTime] - $logString"
}

# Find a certificate that fulfills all the requirements
$ClientCert=$(Get-ChildItem Cert:\localmachine\TrustedPeople |
  # EnhancedKeyUsages must include 'Client Authentication'
  where-object {
	  $_.Extensions |
		where-object {
			$_.EnhancedKeyUsages |
			  where-object {
				  $_.friendlyname -contains "Client Authentication"
			  }
		}
  } |
  # Certificate must be issued by the specified certification authority
  where-object {
		  $_.Issuer -eq "$Issuer"
  } |
  # Certificate must be issued to the specified subject
  where-object {
		   $($_.Subject.Split(", ") | ? {$_.Startswith("CN=")}).Split("=")[1] -eq "$Subject"
  } |
  # Select the first matching certificate
			  select-object -first 1)

if (!$ClientCert) {
    $Message = 'No matching Client Certificate found!'
    log $Message
	exit 5
}

# Find Root Certificate to use
$RootCert = Get-ChildItem cert:\LocalMachine\Root | ? {$_.Issuer -match $Issuer}
if (!$RootCert) {
	$RootCert = Get-ChildItem cert:\LocalMachine\CA | ? {$_.Issuer -match $Issuer}
	if (!$RootCert) {
		$Message = 'Issuer Certificate not found!'
		log $Message
		exit 5
	}
}
$IssuerThumbprint = $RootCert.Thumbprint

try
{
	Get-WSManInstance winrm/config/service/certmapping -selectorset @{Subject=$Subject;URI="*";Issuer="$IssuerThumbprint"}
	$Message = 'A matching Certificate Mapping already exists for this computer.'
	log $Message
	exit 0
}
catch
{
# An error incidcates a listener doesn't exist so we can install one.
}

$LocalUser = Get-WmiObject -Class Win32_UserAccount -Filter  "LocalAccount='True'" | where-object {$_.Name -eq $Username} | select-object -first 1


$Assembly = Add-Type -AssemblyName System.Web
$Password = [System.Web.Security.Membership]::GeneratePassword(24,8)

if (!$LocalUser) {
    $Message = 'User not found found, creating one.'
    log $Message
	$objOu = [ADSI]"WinNT://$Env:Computername"
	$objUser = $objOU.Create("User", $Username)
	$objUser.setpassword($Password)
	$objUser.fullname = "arago HIRO"
	$objUser.description = "Service Account for the arago HIRO automation suite"
	$objUser.UserFlags = 64 + 65536 # ADS_UF_PASSWD_CANT_CHANGE + ADS_UF_DONT_EXPIRE_PASSWD
	$objUser.SetInfo()
	# Add to local Administrator's group
	$objGroup = [ADSI]"WinNT://$Env:Computername/Administrators,group"
	$objGroup.Add("WinNT://$Env:Computername/$Username")
	
} else {
    $Message = 'User found found, resetting pw'
    log $Message
	# local user exists but no mapping -> reset pw
    $objUser = [ADSI]"WinNT://$Env:Computername/$Username"
	$objUser.setpassword($Password)
	$objUser.fullname = "arago HIRO"
	$objUser.description = "Service Account for the arago HIRO automation suite"
	$objUser.UserFlags = 64 + 65536 # ADS_UF_PASSWD_CANT_CHANGE + ADS_UF_DONT_EXPIRE_PASSWD
	$objUser.SetInfo()
	# Add to local Administrator's group
    if (!$(net localgroup administrators | Where {$_ -match $Username}))
	{
		log "Adding User to local Administrator's group"
		$objGroup = [ADSI]"WinNT://$Env:Computername/Administrators,group"
		$objGroup.Add("WinNT://$Env:Computername/$Username")
	}
	else {
		log "User already belongs to local Administrator's group"
	}
}

try
{
	$SecurePassword=ConvertTo-SecureString $password -AsPlainText -Force
	$cred = new-object -typename System.Management.Automation.PSCredential -argumentlist $Username,$SecurePassword
	New-Item -Path WSMan:\localhost\ClientCertificate -Credential $cred -Subject $Subject -URI * -Issuer $IssuerThumbprint -Force
} catch {
	log "Creating certificate mapping failed"
	exit 5
}

try
{
	log "Enabling client certificate authentication"
	Set-Item -Path WSMan:\localhost\Service\Auth\Certificate -Value $true
} catch {
	log "Enabling client certificate authentication failed!"
	exit 5
}
