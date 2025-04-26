$outputDir = "$PWD\output"
$outputFile = "$outputDir\ServicesReport.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# --- Gather Service Information with Error Handling ---
$ErrorActionPreference = "SilentlyContinue"
$services = $null
$errorMessage = $null

try {
    # Get all required info efficiently from Win32_Service
    $services = Get-WmiObject -Class Win32_Service -ErrorAction Stop |
        Select-Object DisplayName, Name, State, StartMode, StartName, Description, PathName |
        Sort-Object DisplayName # Sort by Display Name
} catch {
    Write-Warning "Failed to get Win32_Service info: $($_.Exception.Message)"
    $errorMessage = "Error retrieving service information: $($_.Exception.Message)"
}

# --- Generate HTML Content ---
$htmlBodyContent = ""
if ($errorMessage) {
    $htmlBodyContent = "<h2>Windows Services Report</h2><p style='color:red;'>$errorMessage</p>"
} elseif ($services) {
    $tableRows = ""
    foreach ($service in $services) {
        # Sanitize potential nulls or empty strings for display
        $displayName = $service.DisplayName | Out-String -Stream
        $serviceName = $service.Name | Out-String -Stream
        $status = $service.State | Out-String -Stream
        $startType = $service.StartMode | Out-String -Stream
        $startName = $service.StartName | Out-String -Stream
        $description = $service.Description | Out-String -Stream
        $pathName = $service.PathName | Out-String -Stream

        $tableRows += @"
        <tr>
            <td>$($displayName)</td>
            <td>$($serviceName)</td>
            <td>$($status)</td>
            <td>$($startType)</td>
            <td>$($startName)</td>
            <td>$($description)</td>
            <td>$($pathName)</td>
        </tr>
"@
    }

    $htmlBodyContent = @"
    <h2>Windows Services Report</h2>
    <table class="table table-striped table-bordered table-hover"> <!-- Added Bootstrap classes -->
        <thead>
            <tr>
                <th>Display Name</th>
                <th>Service Name</th>
                <th>Status (State)</th>
                <th>Start Type (Mode)</th>
                <th>Log On As (Start Name)</th>
                <th>Description</th>
                <th>Path Name</th>
            </tr>
        </thead>
        <tbody>
            $tableRows
        </tbody>
    </table>
"@
} else {
     $htmlBodyContent = "<h2>Windows Services Report</h2><p>No services found or data could not be retrieved.</p>"
}

# --- Construct Full HTML Page ---
$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Windows Services Report</title>
    <!-- Basic Styling (Optional, as index.html applies Bootstrap) -->
    <style>
        /* Minimal styles if viewed directly */
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; word-break: break-all; } /* Allow long paths/desc to wrap */
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
