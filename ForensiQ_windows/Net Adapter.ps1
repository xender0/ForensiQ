$netAdapters = Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, MacAddress, LinkSpeed

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Network Adapters Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Network Adapters Report</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Interface Description</th>
            <th>Status</th>
            <th>MAC Address</th>
            <th>Link Speed</th>
        </tr>
"@

foreach ($adapter in $netAdapters) {
    $html += "<tr>
        <td>$($adapter.Name)</td>
        <td>$($adapter.InterfaceDescription)</td>
        <td>$($adapter.Status)</td>
        <td>$($adapter.MacAddress)</td>
        <td>$($adapter.LinkSpeed)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\NetworkAdaptersReport.html"
$html | Out-File -Encoding utf8 -FilePath $path
