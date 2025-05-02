#Requires -RunAsAdministrator

# --- Configuration ---
$OutputDirectory = ".\output"
$OutputFileName = "Insecure_WiFi_Report.html"

# --- Main Script Logic ---

# 1. Prepare Output Directory
Write-Host "Preparing output directory..."
if (-not (Test-Path $OutputDirectory)) {
    try {
        New-Item -ItemType Directory -Path $OutputDirectory -Force -ErrorAction Stop | Out-Null
    } catch {
        Write-Error "Failed to create output directory '$OutputDirectory'. Please ensure you have permissions. Error: $($_.Exception.Message)"
        Exit 1
    }
}

# 2. Get Wi-Fi Profiles
Write-Host "Retrieving saved Wi-Fi profiles..."
$profiles = @() # Initialize as empty array
try {
    # Get-WlanProfile might not be available on Server Core or if WLAN service is disabled
    $profiles = Get-WlanProfile -ErrorAction Stop
} catch {
    Write-Warning "Could not retrieve Wi-Fi profiles using Get-WlanProfile. Error: $($_.Exception.Message)"
    Write-Warning "Attempting fallback using 'netsh wlan show profiles'..."
    try {
        $netshOutput = netsh wlan show profiles | Out-String
        # Extract profile names using regex
        $profileNames = $netshOutput | Select-String -Pattern 'All User Profile\s+:\s*(.+)' | ForEach-Object { $_.Matches[0].Groups[1].Value.Trim() }
        # Create mock profile objects for consistency
        $profiles = $profileNames | ForEach-Object { [PSCustomObject]@{ Name = $_ } }
    } catch {
         Write-Error "Failed to retrieve profiles using netsh as well. Error: $($_.Exception.Message)"
         # Create an empty report indicating failure
         $reportPath = Join-Path $OutputDirectory $OutputFileName
         $htmlContent = @"
<!DOCTYPE html><html><head><title>Insecure Wi-Fi Report</title></head><body>
<h1>Insecure Wi-Fi Report</h1><p>Generated: $(Get-Date)</p>
<p style='color:red;'><b>Error: Failed to retrieve any Wi-Fi profiles. Cannot perform check.</b></p>
</body></html>
"@
         $htmlContent | Out-File -FilePath $reportPath -Encoding UTF8
         Write-Error "Exiting script due to failure in retrieving profiles."
         Exit 1
    }
}

if ($profiles.Count -eq 0) {
    Write-Host "No saved Wi-Fi profiles found on this system."
     # Create an empty report indicating none found
     $reportPath = Join-Path $OutputDirectory $OutputFileName
     $htmlContent = @"
<!DOCTYPE html><html><head><title>Insecure Wi-Fi Report</title></head><body>
<h1>Insecure Wi-Fi Report</h1><p>Generated: $(Get-Date)</p>
<p>No saved Wi-Fi profiles were found on this system.</p>
</body></html>
"@
     $htmlContent | Out-File -FilePath $reportPath -Encoding UTF8
    Exit 0
}

Write-Host "Found $($profiles.Count) profiles. Checking security settings..."
$insecureProfiles = @() # Array to store results

# 3. Check Each Profile's Security
$i = 0
foreach ($profile in $profiles) {
    $i++
    $profileName = $profile.Name
    Write-Host " ($i/$($profiles.Count)) Checking profile: '$profileName'..."

    $authType = $null
    $cipherType = $null

    try {
        # Execute netsh to get profile details
        # Using ErrorAction SilentlyContinue as some profiles might be corrupted/unreadable
        $netshOutputLines = netsh wlan show profile name="$profileName" key=clear # key=clear sometimes reveals more, but not strictly needed for Auth/Cipher
        #$netshOutputLines = netsh wlan show profile name="$profileName"

        # Parse the output line by line
        foreach ($line in $netshOutputLines) {
            # Use regex to capture the value after the colon, trimming whitespace
            if ($line -match '^\s*Authentication\s*:\s*(.+)$') {
                $authType = $matches[1].Trim()
            }
            if ($line -match '^\s*Cipher\s*:\s*(.+)$') {
                $cipherType = $matches[1].Trim()
            }
            # Optimization: Stop parsing if both found
            if ($authType -and $cipherType) {
                break
            }
        }

        # Check if it matches WPA/TKIP criteria
        # Be inclusive of variations like WPA-Personal, WPAPSK, WPA
        if (($authType -eq 'WPA' -or $authType -like 'WPA-Personal*' -or $authType -like 'WPAPSK*') -and $cipherType -eq 'TKIP') {
            Write-Host "  -> Found Insecure WPA/TKIP configuration for '$profileName'" -ForegroundColor Yellow
            $insecureProfiles += [PSCustomObject]@{
                ProfileName    = $profileName
                Authentication = $authType
                Cipher         = $cipherType
            }
        } else {
             Write-Verbose "  Profile '$profileName' (Auth: $authType, Cipher: $cipherType) is not WPA/TKIP."
        }

    } catch {
        Write-Warning "Could not process profile '$profileName'. Error: $($_.Exception.Message)"
    }
}

# 4. Generate HTML Report
Write-Host "Generating HTML report..."
$reportPath = Join-Path $OutputDirectory $OutputFileName

# Basic HTML Header and Style
$htmlHeader = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Insecure Wi-Fi Report (WPA/TKIP)</title>
    <style>
        body { font-family: sans-serif; }
        table { border-collapse: collapse; width: 60%; margin-top: 15px;}
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #e2e2e2; }
        .warning { color: orange; font-weight: bold; }
        .profile-name { font-weight: bold; }
    </style>
</head>
<body>
<h1>Insecure Wi-Fi Report (WPA/TKIP)</h1>
<p>Generated: $(Get-Date)</p>
"@

$htmlFooter = @"
</body>
</html>
"@

$htmlBody = ""
if ($insecureProfiles.Count -gt 0) {
    $htmlBody = "<p class='warning'>The following saved Wi-Fi profiles were found using the insecure WPA/TKIP security configuration:</p>"
    # Select properties and rename for clarity in the report
    $htmlTable = $insecureProfiles | Select-Object @{Name='Profile Name';Expression={$_.ProfileName}}, @{Name='Authentication Type';Expression={$_.Authentication}}, @{Name='Cipher Type';Expression={$_.Cipher}} | ConvertTo-Html -Fragment
    $htmlBody += $htmlTable
} else {
    $htmlBody = "<p>No saved Wi-Fi profiles using insecure WPA/TKIP configurations were found.</p>"
}

# Combine and Save
$htmlContent = $htmlHeader + $htmlBody + $htmlFooter
try {
    $htmlContent | Out-File -FilePath $reportPath -Encoding UTF8 -ErrorAction Stop
    Write-Host "HTML report saved to '$reportPath'" -ForegroundColor Green
} catch {
    Write-Error "Failed to save HTML report to '$reportPath': $($_.Exception.Message)"
}

Write-Host "Script finished."
