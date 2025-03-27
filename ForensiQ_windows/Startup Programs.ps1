$startupCommands = Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Startup Programs Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Startup Programs Report</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Command</th>
            <th>Location</th>
        </tr>
"@

foreach ($command in $startupCommands) {
    $html += "<tr>
        <td>$($command.Name)</td>
        <td>$($command.Command)</td>
        <td>$($command.Location)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\StartupProgramsReport.html"
$html | Out-File -Encoding utf8 -FilePath $path