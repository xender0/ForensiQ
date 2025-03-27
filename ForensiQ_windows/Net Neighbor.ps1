$data = Get-NetNeighbor | Select-Object InterfaceAlias, IPAddress, LinkLayerAddress

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Network Neighbors Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Network Neighbors Report</h2>
    <table>
        <tr>
            <th>Interface Alias</th>
            <th>IPAddress</th>
            <th>LinkLayerAddress</th>
        </tr>
"@

foreach ($entry in $data) {
    $html += "<tr>
        <td>$($entry.InterfaceAlias)</td>
        <td>$($entry.IPAddress)</td>
        <td>$($entry.LinkLayerAddress)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\NetworkNeighborsReport.html"
$html | Out-File -Encoding utf8 -FilePath $path
