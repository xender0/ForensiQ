$data = Get-ScheduledTask | Select-Object TaskPath, TaskName, State

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Scheduled Tasks Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Scheduled Tasks Report</h2>
    <table>
        <tr>
            <th>Task Path</th>
            <th>Task Name</th>
            <th>State</th>
        </tr>
"@

foreach ($task in $data) {
    $html += "<tr>
        <td>$($task.TaskPath)</td>
        <td>$($task.TaskName)</td>
        <td>$($task.State)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\ScheduledTasksReport.html"
$html | Out-File -Encoding utf8 -FilePath $path
