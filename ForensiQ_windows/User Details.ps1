$systemInfo = Get-WmiObject -Class Win32_ComputerSystem | 
              Select-Object Name, DNSHostName, Domain, Manufacturer, Model, PrimaryOwnerName, TotalPhysicalMemory, Workgroup

$outputDir = "$PWD\output"
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>System Information Report</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }
        .container { width: 60%; margin: auto; padding: 20px; border: 1px solid black; border-radius: 10px; background-color: #ffffff; }
        h2 { text-align: center; }
        p { font-size: 16px; }
        strong { color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h2>System Information Report</h2>
        <p><strong>Name:</strong> $($systemInfo.Name)</p>
        <p><strong>DNS Host Name:</strong> $($systemInfo.DNSHostName)</p>
        <p><strong>Domain:</strong> $($systemInfo.Domain)</p>
        <p><strong>Manufacturer:</strong> $($systemInfo.Manufacturer)</p>
        <p><strong>Model:</strong> $($systemInfo.Model)</p>
        <p><strong>Primary Owner Name:</strong> $($systemInfo.PrimaryOwnerName)</p>
        <p><strong>Total Physical Memory:</strong> $([math]::Round($systemInfo.TotalPhysicalMemory / 1GB, 2)) GB</p>
        <p><strong>Workgroup:</strong> $($systemInfo.Workgroup)</p>
    </div>
</body>
</html>
"@

$path = Join-Path -Path $outputDir -ChildPath "UserDetails.html"
$html | Out-File -Encoding utf8 -FilePath $path

Write-Host "UserDetails.html has been generated at: $path"
