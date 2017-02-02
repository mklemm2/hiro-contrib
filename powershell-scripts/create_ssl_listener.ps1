[CmdLetBinding()]
param
(
    [Parameter(Mandatory=$true)]
    [String] $Issuer,

    [Int] $Port = 5986
)

$Logfile = "c:\windows\logs\create_ssl_listener.log"

Function log
{
	Param ([string]$logstring)

	$nowDate = Get-Date -format dd.MM.yyyy
    $nowTime = Get-Date -format HH:mm:ss
	write-verbose -message $logstring
	Add-content $Logfile -value "[$nowDate][$nowTime] - $logString"
}

try
{
    Get-WSManInstance  -ResourceURI winrm/config/Listener  -SelectorSet @{Address='*';Transport='HTTPS'}
    $Message = 'An HTTPS WinRM Listener already exists for this computer.'
    log $Message
    exit 0
}
catch
{
# An error incidcates a listener doesn't exist so we can install one.
}

[String] $HostName = [System.Net.Dns]::GetHostByName($ENV:computerName).Hostname

# Find the correct certificate for the SSL listener
$ServerCert=$(Get-ChildItem Cert:\localmachine\my |
  # Only server certificates
  where-object {
	  $_.Extensions |
		where-object {
			$_.EnhancedKeyUsages |
			  where-object {
				  $_.friendlyname -contains "Server Authentication"
			  }
		}
  } |
  # Only certificates issued by the correct CA
  where-object {
		  $_.Issuer -eq "$Issuer"
  } |
  # Only certificates with Subject or Subject Alternative Name matching our DNS Name
  where-object {
	  ($_.Subject -eq "CN=$HostName") -or $($_.Extensions|
		where-object {
			$_.oid.friendlyname -eq "Subject Alternative Name"
		}
	   ).Format(0) -match "DNS Name=$HostName"
  } |
  # Select the first matching certificate
  select-object -first 1)




# Exit if the required certificates are not there
if (!$ServerCert) {
    $Message = 'No matching Server Certificate found!'
    log $Message
	exit 5
}


# Start WinRM service
$Message = "Starting WinRM service"
log $Message
Set-Service winrm -StartupType Automatic -Status Running

$Message = "Creating new HTTPS WinRM Listener for '$Hostname' with certificate '" + $ServerCert.Thumbprint + "'." 
log $Message
try {
	New-WSManInstance `
      -ResourceURI winrm/config/Listener `
      -SelectorSet @{Address='*';Transport='HTTPS'} `
      -ValueSet @{Hostname=$HostName;CertificateThumbprint=$ServerCert.Thumbprint;Port=$Port} `
      -ErrorAction Stop
	$Message = "The new HTTPS WinRM Listener for '$Hostname' with certificate '" + $ServerCert.Thumbprint + "' has been created."
    log $Message
	exit 0
    } catch {
	$Message = $_
	log $Message
	exit 5
}
