$outputDir = Join-Path -Path $PWD -ChildPath "output"
$outputFile = Join-Path -Path $outputDir -ChildPath "NetworkAdapters.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# --- Helper Functions ---
Function Get-AvailabilityDescription {
    param($code)
    switch ($code) {
        1 { "Other" }
        2 { "Unknown" }
        3 { "Running/Full Power" }
        4 { "Warning" }
        5 { "In Test" }
        6 { "Not Applicable" }
        7 { "Power Off" }
        8 { "Off Line" }
        9 { "Off Duty" }
        10 { "Degraded" }
        11 { "Not Installed" }
        12 { "Install Error" }
        13 { "Power Save - Unknown" }
        14 { "Power Save - Low Power Mode" }
        15 { "Power Save - Standby" }
        16 { "Power Cycle" }
        17 { "Power Save - Warning" }
        18 { "Paused" }
        19 { "Not Ready" }
        20 { "Not Configured" }
        21 { "Quiesced" }
        default { "Unknown ($code)" }
    }
}

Function Get-NetConnectionStatusDescription {
    param($code)
    switch ($code) {
        0 { "Disconnected" }
        1 { "Connecting" }
        2 { "Connected" }
        3 { "Disconnecting" }
        4 { "Hardware Not Present" }
        5 { "Hardware Disabled" }
        6 { "Hardware Malfunction" }
        7 { "Media Disconnected" }
        8 { "Authenticating" }
        9 { "Authentication Succeeded" }
        10 { "Authentication Failed" }
        11 { "Invalid Address" }
        12 { "Credentials Required" }
        default { "Unknown ($code)" }
    }
}

Function Convert-BooleanToYesNo {
    param($value)
    if ($value -eq $null) { return "N/A" }
    if ($value -eq $true) { return "Yes" } else { return "No" }
}

# --- Gather Network Adapter Information with Error Handling ---
$ErrorActionPreference = "SilentlyContinue"
$networkAdapters = $null
$errorMessage = $null

try {
    # Added InterfaceIndex, Speed, NetConnectionID for more context
    $networkAdapters = Get-WmiObject -class Win32_NetworkAdapter -ErrorAction Stop |
        Select-Object AdapterType, ProductName, Description, MACAddress, Availability, NetconnectionStatus, NetEnabled, PhysicalAdapter, InterfaceIndex, Speed, NetConnectionID
} catch {
    Write-Warning "Failed to get Win32_NetworkAdapter info: $($_.Exception.Message)"
    $errorMessage = "Error retrieving network adapter information: $($_.Exception.Message)"
}

# --- Generate HTML Content ---
$htmlBodyContent = ""
if ($errorMessage) {
    $htmlBodyContent = "<h2>Network Adapters</h2><p style='color:red;'>$errorMessage</p>"
} elseif ($networkAdapters) {
    $tableRows = ""
    foreach ($adapter in $networkAdapters) {
        $availabilityDesc = Get-AvailabilityDescription $adapter.Availability
        $statusDesc = Get-NetConnectionStatusDescription $adapter.NetconnectionStatus
        $enabled = Convert-BooleanToYesNo $adapter.NetEnabled
        $physical = Convert-BooleanToYesNo $adapter.PhysicalAdapter
        # Format Speed (convert bps to Mbps/Gbps if available)
        $speedFormatted = if ($adapter.Speed -ne $null) {
            if ($adapter.Speed -ge 1000000000) { "$([Math]::Round($adapter.Speed / 1000000000, 1)) Gbps" }
            elseif ($adapter.Speed -ge 1000000) { "$([Math]::Round($adapter.Speed / 1000000)) Mbps" }
            else { "$($adapter.Speed) bps" }
        } else { "N/A" }

        $tableRows += @"
        <tr>
            <td>$($adapter.InterfaceIndex)</td>
            <td>$($adapter.NetConnectionID)</td>
            <td>$($adapter.ProductName)</td>
            <td>$($adapter.Description)</td>
            <td>$($adapter.AdapterType)</td>
            <td>$($adapter.MACAddress)</td>
            <td>$($statusDesc)</td>
            <td>$($enabled)</td>
            <td>$($physical)</td>
            <td>$($availabilityDesc)</td>
            <td>$($speedFormatted)</td>
        </tr>
"@
    }

    $htmlBodyContent = @"
    <h2>Network Adapters</h2>
    <table class="table table-striped table-bordered table-hover"> <!-- Added Bootstrap classes -->
        <thead>
            <tr>
                <th>Index</th>
                <th>Connection ID</th>
                <th>Product Name</th>
                <th>Description</th>
                <th>Adapter Type</th>
                <th>MAC Address</th>
                <th>Status</th>
                <th>Enabled</th>
                <th>Physical</th>
                <th>Availability</th>
                <th>Speed</th>
            </tr>
        </thead>
        <tbody>
            $tableRows
        </tbody>
    </table>
"@
} else {
     $htmlBodyContent = "<h2>Network Adapters</h2><p>No network adapters found or data could not be retrieved.</p>"
}

# --- Construct Full HTML Page ---
$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Network Adapters</title>
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
