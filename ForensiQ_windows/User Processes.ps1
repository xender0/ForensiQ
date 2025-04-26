$outputDir = "$PWD\output"
$outputFile = "$outputDir\ProcessList.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# --- Helper Function to Format Bytes ---
Function Format-Bytes {
    param($bytes)
    if ($bytes -eq $null -or $bytes -lt 0) { return "N/A" }
    # Using MB as the base unit for process memory seems reasonable
    if ($bytes -ge 1GB) { return "$([Math]::Round($bytes / 1GB, 2)) GB" }
    if ($bytes -ge 1MB) { return "$([Math]::Round($bytes / 1MB, 2)) MB" }
    if ($bytes -ge 1KB) { return "$([Math]::Round($bytes / 1KB, 2)) KB" }
    return "$bytes Bytes"
}

# --- Gather Process Information with Error Handling ---
$ErrorActionPreference = "SilentlyContinue"
$processes = $null
$errorMessage = $null

try {
    # Added StartTime
    $processes = Get-Process -IncludeUserName -ErrorAction Stop |
        Select-Object Name, Id, UserName, CPU, WorkingSet, Path, StartTime |
        Sort-Object Name, StartTime # Sort by Name, then StartTime
} catch {
    Write-Warning "Failed to get process info: $($_.Exception.Message)"
    $errorMessage = "Error retrieving process information: $($_.Exception.Message)"
}

# --- Generate HTML Content ---
$htmlBodyContent = ""
if ($errorMessage) {
    $htmlBodyContent = "<h2>Process List</h2><p style='color:red;'>$errorMessage</p>"
} elseif ($processes) {
    $tableRows = ""
    foreach ($process in $processes) {
        # Format values
        $memoryFormatted = Format-Bytes $process.WorkingSet
        $cpuFormatted = if ($process.CPU -ne $null) { [Math]::Round($process.CPU, 2) } else { "N/A" }
        $startTimeFormatted = if ($process.StartTime -ne $null) { $process.StartTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "N/A" }
        $userName = $process.UserName # Already retrieved by -IncludeUserName
        $path = $process.Path | Out-String -Stream # Handle potential null/empty

        $tableRows += @"
        <tr>
            <td>$($process.Name)</td>
            <td>$($process.Id)</td>
            <td>$($userName)</td>
            <td>$($cpuFormatted)</td>
            <td>$($memoryFormatted)</td>
            <td>$($startTimeFormatted)</td>
            <td>$($path)</td>
        </tr>
"@
    }

    $htmlBodyContent = @"
    <h2>Process List</h2>
    <table class="table table-striped table-bordered table-hover"> <!-- Added Bootstrap classes -->
        <thead>
            <tr>
                <th>Name</th>
                <th>Id</th>
                <th>User Name</th>
                <th>CPU (s)</th>
                <th>Memory (Working Set)</th>
                <th>Start Time</th>
                <th>Path</th>
            </tr>
        </thead>
        <tbody>
            $tableRows
        </tbody>
    </table>
"@
} else {
     $htmlBodyContent = "<h2>Process List</h2><p>No processes found or data could not be retrieved.</p>"
}

# --- Construct Full HTML Page ---
$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Process List</title>
    <!-- Basic Styling (Optional, as index.html applies Bootstrap) -->
    <style>
        /* Minimal styles if viewed directly */
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; word-break: break-all; } /* Allow long paths to wrap */
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
