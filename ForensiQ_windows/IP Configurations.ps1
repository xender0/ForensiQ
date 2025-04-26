$outputDir = "$PSScriptRoot\output"
if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$htmlFile = "$outputDir\NetworkInfo.html"

$networkInfo = Get-WmiObject Win32_NetworkAdapterConfiguration | Select-Object Description, 
    @{Name = 'IpAddress'; Expression = { $_.IpAddress -join '; ' } }, 
    @{Name = 'IpSubnet'; Expression = { $_.IpSubnet -join '; ' } }, 
    MACAddress, 
    @{Name = 'DefaultIPGateway'; Expression = { $_.DefaultIPGateway -join '; ' } }, 
    DNSDomain, DNSHostName, DHCPEnabled, ServiceName

$htmlHeader = @"
<html>
<head>
    <title>Network Adapter Information</title>
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Network Adapter Information</h2>
    <table>
        <tr>
            <th>Description</th>
            <th>IP Address</th>
            <th>IP Subnet</th>
            <th>MAC Address</th>
            <th>Default Gateway</th>
            <th>DNS Domain</th>
            <th>DNS Hostname</th>
            <th>DHCP Enabled</th>
            <th>Service Name</th>
        </tr>
"@

$htmlBody = ""
foreach ($adapter in $networkInfo) {
    $htmlBody += "<tr>"
    $htmlBody += "<td>$($adapter.Description)</td>"
    $htmlBody += "<td>$($adapter.IpAddress)</td>"
    $htmlBody += "<td>$($adapter.IpSubnet)</td>"
    $htmlBody += "<td>$($adapter.MACAddress)</td>"
    $htmlBody += "<td>$($adapter.DefaultIPGateway)</td>"
    $htmlBody += "<td>$($adapter.DNSDomain)</td>"
    $htmlBody += "<td>$($adapter.DNSHostName)</td>"
    $htmlBody += "<td>$($adapter.DHCPEnabled)</td>"
    $htmlBody += "<td>$($adapter.ServiceName)</td>"
    $htmlBody += "</tr>"
}

$htmlFooter = @"
    </table>
</body>
</html>
"@

$htmlContent = $htmlHeader + $htmlBody + $htmlFooter
$htmlContent | Out-File -Encoding UTF8 -FilePath $htmlFile

Write-Output "HTML report saved to: $htmlFile"