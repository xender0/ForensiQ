$status = Get-MpComputerStatus | Select-Object -Property `
    AMProductVersion, AMRunningMode, AMServiceEnabled, AntispywareEnabled, 
    AntispywareSignatureLastUpdated, AntivirusEnabled, AntivirusSignatureLastUpdated, 
    BehaviorMonitorEnabled, DefenderSignaturesOutOfDate, DeviceControlPoliciesLastUpdated, 
    DeviceControlState, NISSignatureLastUpdated, QuickScanEndTime, RealTimeProtectionEnabled

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Windows Defender Status</title>
</head>
<body>
    <h2>Windows Defender Status</h2>
    <table border="1">
        <tr><th>Property</th><th>Value</th></tr>
"@

foreach ($prop in $status.PSObject.Properties) {
    $html += @"
        <tr>
            <td>$($prop.Name)</td>
            <td>$($prop.Value)</td>
        </tr>
"@
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\DefenderStatus.html"
$html | Out-File -Encoding utf8 -FilePath $path