$dnsCache = Get-DnsClientCache | Select-Object Entry, Name, Status, TimeToLive, Data

$html = @"
<html>
<head>
    <title>DNS Client Cache</title>
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>DNS Client Cache</h2>
    <table>
        <tr>
            <th>Entry</th>
            <th>Name</th>
            <th>Status</th>
            <th>TimeToLive</th>
            <th>Data</th>
        </tr>
"@

foreach ($entry in $dnsCache) {
    $html += "<tr>"
    $html += "<td>$($entry.Entry)</td>"
    $html += "<td>$($entry.Name)</td>"
    $html += "<td>$($entry.Status)</td>"
    $html += "<td>$($entry.TimeToLive)</td>"
    $html += "<td>$($entry.Data)</td>"
    $html += "</tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$currentDirectory = Get-Location
$html | Out-File -Encoding utf8 -FilePath "$currentDirectory\output\dns_cache.html"

Write-Output "DNS cache has been saved to $currentDirectory\output\dns_cache.html"