$outputDir = "$PWD\output"
$outputFile = "$outputDir\Administrators.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

$groupMembers = Get-LocalGroupMember -Group "Administrators" | 
    Select-Object ObjectClass, Name, PrincipalSource

$htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Administrators Group Members</title>
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Administrators Group Members</h2>
    <table>
        <tr>
            <th>ObjectClass</th>
            <th>Name</th>
            <th>PrincipalSource</th>
        </tr>
"@

foreach ($member in $groupMembers) {
    $htmlContent += "<tr><td>$($member.ObjectClass)</td><td>$($member.Name)</td><td>$($member.PrincipalSource)</td></tr>`n"
}

$htmlContent += @"
    </table>
</body>
</html>
"@

$htmlContent | Out-File -Encoding UTF8 -FilePath $outputFile

Write-Output "Results saved to: $outputFile"
