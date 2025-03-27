$localGroups = Get-LocalGroup | Select-Object Name, Description

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Local Groups Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Local Groups Report</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Description</th>
        </tr>
"@

foreach ($group in $localGroups) {
    $html += "<tr>
        <td>$($group.Name)</td>
        <td>$($group.Description)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\LocalGroupsReport.html"
$html | Out-File -Encoding utf8 -FilePath $path