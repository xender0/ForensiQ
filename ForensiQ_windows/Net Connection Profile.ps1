$netProfiles = Get-NetConnectionProfile | Select-Object Name, InterfaceAlias, NetworkCategory, IPv4Connectivity, IPv6Connectivity

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Network Connection Profiles Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Network Connection Profiles Report</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Interface Alias</th>
            <th>Network Category</th>
            <th>IPv4 Connectivity</th>
            <th>IPv6 Connectivity</th>
        </tr>
"@

foreach ($profile in $netProfiles) {
    $html += "<tr>
        <td>$($profile.Name)</td>
        <td>$($profile.InterfaceAlias)</td>
        <td>$($profile.NetworkCategory)</td>
        <td>$($profile.IPv4Connectivity)</td>
        <td>$($profile.IPv6Connectivity)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\NetworkConnectionProfilesReport.html"
$html | Out-File -Encoding utf8 -FilePath $path
