$outputDir = "$PWD\output"
$outputFile = "$outputDir\USB_Devices.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

$devices = Get-PnpDevice -PresentOnly -class 'USB', 'DiskDrive', 'Mouse', 'Keyboard', 'Net', 'Image', 'Media', 'Monitor' | 
    Select-Object Status, Class, FriendlyName

$htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Connected Devices</title>
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Connected Devices</h2>
    <table>
        <tr>
            <th>Status</th>
            <th>Class</th>
            <th>Friendly Name</th>
        </tr>
"@

foreach ($device in $devices) {
    $htmlContent += "<tr>
        <td>$($device.Status)</td>
        <td>$($device.Class)</td>
        <td>$($device.FriendlyName)</td>
    </tr>`n"
}

$htmlContent += @"
    </table>
</body>
</html>
"@

$htmlContent | Out-File -Encoding UTF8 -FilePath $outputFile
