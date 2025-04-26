$outputDir = "$PWD\output"
$outputFile = "$outputDir\LogicalDisks.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

# --- Helper Function to Format Bytes ---
Function Format-Bytes {
    param($bytes)
    if ($bytes -eq $null -or $bytes -lt 0) { return "N/A" }
    if ($bytes -ge 1TB) { return "$([Math]::Round($bytes / 1TB, 2)) TB" }
    if ($bytes -ge 1GB) { return "$([Math]::Round($bytes / 1GB, 2)) GB" }
    if ($bytes -ge 1MB) { return "$([Math]::Round($bytes / 1MB, 2)) MB" }
    if ($bytes -ge 1KB) { return "$([Math]::Round($bytes / 1KB, 2)) KB" }
    return "$bytes Bytes"
}

# --- Helper Function to Translate DriveType ---
Function Get-DriveTypeDescription {
    param($driveTypeCode)
    switch ($driveTypeCode) {
        0 { "Unknown" }
        1 { "No Root Directory" }
        2 { "Removable Disk" }
        3 { "Local Disk" } # Typically Fixed hard disk
        4 { "Network Drive" }
        5 { "Compact Disc" }
        6 { "RAM Disk" }
        default { "Unknown ($driveTypeCode)" }
    }
}

# --- Gather Disk Information with Error Handling ---
$ErrorActionPreference = "SilentlyContinue"
$disks = $null
$errorMessage = $null

try {
    $disks = Get-WmiObject Win32_LogicalDisk -ErrorAction Stop | Select-Object DeviceID, DriveType, FreeSpace, Size, VolumeName, FileSystem
} catch {
    Write-Warning "Failed to get Win32_LogicalDisk info: $($_.Exception.Message)"
    $errorMessage = "Error retrieving disk information: $($_.Exception.Message)"
}

# --- Generate HTML Content ---
$htmlBodyContent = ""
if ($errorMessage) {
    # If there was an error getting disk info
    $htmlBodyContent = "<h2>Logical Disks</h2><p style='color:red;'>$errorMessage</p>"
} elseif ($disks) {
    # If disks were retrieved successfully
    $tableRows = ""
    foreach ($disk in $disks) {
        $sizeFormatted = Format-Bytes $disk.Size
        $freeSpaceFormatted = Format-Bytes $disk.FreeSpace
        $driveTypeDescription = Get-DriveTypeDescription $disk.DriveType
        $freePercent = if ($disk.Size -gt 0) { [Math]::Round(($disk.FreeSpace / $disk.Size) * 100, 1) } else { 0 }
        $fileSystem = $disk.FileSystem | Out-String -Stream # Handle potential null/empty

        $tableRows += @"
        <tr>
            <td>$($disk.DeviceID)</td>
            <td>$($driveTypeDescription)</td>
            <td>$($fileSystem)</td>
            <td>$($sizeFormatted)</td>
            <td>$($freeSpaceFormatted)</td>
            <td>$($freePercent)%</td>
            <td>$($disk.VolumeName)</td>
        </tr>
"@
    }

    $htmlBodyContent = @"
    <h2>Logical Disks</h2>
    <table class="table table-striped table-bordered table-hover"> <!-- Added Bootstrap classes -->
        <thead>
            <tr>
                <th>Device ID</th>
                <th>Drive Type</th>
                <th>File System</th>
                <th>Total Size</th>
                <th>Free Space</th>
                <th>Free (%)</th>
                <th>Volume Name</th>
            </tr>
        </thead>
        <tbody>
            $tableRows
        </tbody>
    </table>
"@
} else {
     $htmlBodyContent = "<h2>Logical Disks</h2><p>No logical disks found or data could not be retrieved.</p>"
}


# --- Construct Full HTML Page ---
$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Logical Disks</title>
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
