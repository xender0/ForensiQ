$outputDir = "$PWD\output"
$outputFile = "$outputDir\TempExeFiles.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

$exeFiles = 
    (Get-ChildItem C:\Users\*\AppData\Local\Temp\* -Recurse -ErrorAction SilentlyContinue) + 
    (Get-ChildItem C:\PerfLogs\* -Recurse -ErrorAction SilentlyContinue) | 
    Where-Object { $_.Extension -eq '.exe' } | 
    Select-Object PSChildName, Root, Name, FullName, Extension, CreationTimeUTC, LastAccessTimeUTC, LastWriteTimeUTC, Attributes

$htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Temporary Executable Files</title>
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        td { word-wrap: break-word; max-width: 300px; }
    </style>
</head>
<body>
    <h2>Temporary Executable Files</h2>
    <table>
        <tr>
            <th>PSChildName</th>
            <th>Name</th>
            <th>Full Path</th>
            <th>Extension</th>
            <th>Creation Time (UTC)</th>
            <th>Last Access Time (UTC)</th>
            <th>Last Write Time (UTC)</th>
            <th>Attributes</th>
        </tr>
"@

foreach ($file in $exeFiles) {
    $htmlContent += "<tr>
        <td>$($file.PSChildName)</td>
        <td>$($file.Name)</td>
        <td>$($file.FullName)</td>
        <td>$($file.Extension)</td>
        <td>$($file.CreationTimeUTC)</td>
        <td>$($file.LastAccessTimeUTC)</td>
        <td>$($file.LastWriteTimeUTC)</td>
        <td>$($file.Attributes)</td>
    </tr>`n"
}

$htmlContent += @"
    </table>
</body>
</html>
"@

$htmlContent | Out-File -Encoding UTF8 -FilePath $outputFile
