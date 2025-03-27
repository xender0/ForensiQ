$outputDir = "$PWD\output"
$outputFile = "$outputDir\Cameras.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

$cameraDevices = Get-WmiObject Win32_PnPEntity | 
    Where-Object { $_.Caption -match 'camera' } -EA SilentlyContinue | 
    Select-Object Caption, CreationClassName, Description, DeviceID, InstallDate, Manufacturer, Present, Status, SystemCreationClassName, SystemName

$htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Camera Devices</title>
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Camera Devices</h2>
    <table>
        <tr>
            <th>Caption</th>
            <th>CreationClassName</th>
            <th>Description</th>
            <th>DeviceID</th>
            <th>InstallDate</th>
            <th>Manufacturer</th>
            <th>Present</th>
            <th>Status</th>
            <th>SystemCreationClassName</th>
            <th>SystemName</th>
        </tr>
"@

foreach ($device in $cameraDevices) {
    $htmlContent += "<tr>
        <td>$($device.Caption)</td>
        <td>$($device.CreationClassName)</td>
        <td>$($device.Description)</td>
        <td>$($device.DeviceID)</td>
        <td>$($device.InstallDate)</td>
        <td>$($device.Manufacturer)</td>
        <td>$($device.Present)</td>
        <td>$($device.Status)</td>
        <td>$($device.SystemCreationClassName)</td>
        <td>$($device.SystemName)</td>
    </tr>`n"
}

$htmlContent += @"
    </table>
</body>
</html>
"@

$htmlContent | Out-File -Encoding UTF8 -FilePath $outputFile

Write-Output "Results saved to: $outputFile"
