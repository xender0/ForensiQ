$data = Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess, @{Name = "Process"; Expression = { (Get-Process -Id $_.OwningProcess).ProcessName } }

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>TCP Connections Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>TCP Connections Report</h2>
    <table>
        <tr>
            <th>Local Address</th>
            <th>Local Port</th>
            <th>Remote Address</th>
            <th>Remote Port</th>
            <th>State</th>
            <th>Owning Process</th>
            <th>Process</th>
        </tr>
"@

foreach ($entry in $data) {
    $html += "<tr>
        <td>$($entry.LocalAddress)</td>
        <td>$($entry.LocalPort)</td>
        <td>$($entry.RemoteAddress)</td>
        <td>$($entry.RemotePort)</td>
        <td>$($entry.State)</td>
        <td>$($entry.OwningProcess)</td>
        <td>$($entry.Process)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\TCPConnectionsReport.html"
$html | Out-File -Encoding utf8 -FilePath $path
