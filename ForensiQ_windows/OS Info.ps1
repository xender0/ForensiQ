$data = Get-WmiObject -Class Win32_OperatingSystem | Select-Object -Property Name, Description, Version, BuildNumber, InstallDate, SystemDrive, SystemDevice, WindowsDirectory, LastBootupTime, Locale, LocalDateTime, NumberofUsers, RegisteredUser, Organization, OSProductSuite

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Operating System Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 80%; margin: 20px auto; border-collapse: collapse; }
        th, td { padding: 8px 12px; border: 1px solid #ccc; text-align: left; }
        th { background-color: #eee; }
        h2 { text-align: center; }
    </style>
</head>
<body>
    <h2>Operating System Report</h2>
    <table>
        <thead>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
"@

foreach ($property in $data.PSObject.Properties) {
    $html += "<tr><td>$($property.Name)</td><td>$($property.Value)</td></tr>"
}

$html += @" 
        </tbody>
    </table>
</body>
</html>
"@

$path = "$PWD\output\OSReport.html"
$html | Out-File -Encoding utf8 -FilePath $path
