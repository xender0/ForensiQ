$ipAddresses = Get-NetIPAddress | Select-Object InterfaceAlias, IPAddress, EnabledState, OperatingStatus

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Network IP Address Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Network IP Address Report</h2>
    <table>
        <tr>
            <th>Interface Alias</th>
            <th>IP Address</th>
            <th>Enabled State</th>
            <th>Operating Status</th>
        </tr>
"@

foreach ($ip in $ipAddresses) {
    $html += "<tr>
        <td>$($ip.InterfaceAlias)</td>
        <td>$($ip.IPAddress)</td>
        <td>$($ip.EnabledState)</td>
        <td>$($ip.OperatingStatus)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\NetworkIPReport.html"
$html | Out-File -Encoding utf8 -FilePath $path