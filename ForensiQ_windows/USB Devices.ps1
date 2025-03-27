$usbDevices = Get-ItemProperty -Path HKLM:\System\CurrentControlSet\Enum\USB*\*\* | 
              Select-Object FriendlyName, Driver, Mfg, DeviceDesc

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>USB Devices Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>USB Devices Report</h2>
    <table>
        <tr>
            <th>Friendly Name</th>
            <th>Driver</th>
            <th>Manufacturer</th>
            <th>Device Description</th>
        </tr>
"@

foreach ($device in $usbDevices) {
    $html += "<tr>
        <td>$($device.FriendlyName)</td>
        <td>$($device.Driver)</td>
        <td>$($device.Mfg)</td>
        <td>$($device.DeviceDesc)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\USBDevicesReport.html"
$html | Out-File -Encoding utf8 -FilePath $path