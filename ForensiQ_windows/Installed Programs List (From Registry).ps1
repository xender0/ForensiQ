$outputDir = "$PWD\output"
$outputFile = "$outputDir\InstalledProgramsReport.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# --- Helper Function to Format Install Date ---
Function Format-InstallDate {
    param($regDate)
    if ($regDate -match '^\d{8}$') {
        try {
            return [datetime]::ParseExact($regDate, 'yyyyMMdd', $null).ToString('yyyy-MM-dd')
        } catch {
            return $regDate # Return original if parsing fails
        }
    }
    return $regDate # Return original if not in expected format
}

# --- Gather Installed Programs with Error Handling ---
$ErrorActionPreference = "SilentlyContinue"
$allApps = @()
$errorMessage = $null

# Registry paths to check
$registryPaths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
    # Consider adding HKCU paths if needed:
    # 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    # 'HKCU:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
)

try {
    foreach ($path in $registryPaths) {
        $apps = Get-ItemProperty $path -ErrorAction Stop |
            Where-Object { $_.DisplayName -ne $null -and $_.DisplayName -ne "" } | # Filter out entries without DisplayName
            Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, PSComputerName # Added PSComputerName to distinguish source if needed later
        $allApps += $apps
    }
    # Remove duplicates based on DisplayName, DisplayVersion, and Publisher, then sort
    $installedApps = $allApps | Sort-Object DisplayName, DisplayVersion, Publisher | Select-Object * -Unique
} catch {
    Write-Warning "Failed to get installed programs info: $($_.Exception.Message)"
    $errorMessage = "Error retrieving installed programs information: $($_.Exception.Message)"
}


# --- Generate HTML Content ---
$htmlBodyContent = ""
if ($errorMessage) {
    $htmlBodyContent = "<h2>Installed Programs Report (Registry)</h2><p style='color:red;'>$errorMessage</p>"
} elseif ($installedApps) {
    $tableRows = ""
    foreach ($app in $installedApps) {
        $formattedDate = Format-InstallDate $app.InstallDate
        $tableRows += @"
        <tr>
            <td>$($app.DisplayName)</td>
            <td>$($app.DisplayVersion)</td>
            <td>$($app.Publisher)</td>
            <td>$($formattedDate)</td>
        </tr>
"@
    }

    $htmlBodyContent = @"
    <h2>Installed Programs Report (Registry)</h2>
    <table class="table table-striped table-bordered table-hover"> <!-- Added Bootstrap classes -->
        <thead>
            <tr>
                <th>Display Name</th>
                <th>Version</th>
                <th>Publisher</th>
                <th>Install Date</th>
            </tr>
        </thead>
        <tbody>
            $tableRows
        </tbody>
    </table>
"@
} else {
     $htmlBodyContent = "<h2>Installed Programs Report (Registry)</h2><p>No installed programs found or data could not be retrieved.</p>"
}

# --- Construct Full HTML Page ---
$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Installed Programs Report (Registry)</title>
    <!-- Basic Styling (Optional, as index.html applies Bootstrap) -->
    <style>
        /* Minimal styles if viewed directly */
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    $htmlBodyContent
</body>
</html>
"@

$htmlContent | Out-File -Encoding UTF8 -FilePath $outputFile

Write-Output "Results saved to: $outputFile"
