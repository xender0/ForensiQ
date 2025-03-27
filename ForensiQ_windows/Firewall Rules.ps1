$firewallRules = Get-NetFirewallRule | select-object Name, DisplayName, Description, Direction, Action, EdgeTraversalPolicy, Owner, EnforcementStatus

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Firewall Rules Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Firewall Rules Report</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Display Name</th>
            <th>Description</th>
            <th>Direction</th>
            <th>Action</th>
            <th>Edge Traversal Policy</th>
            <th>Owner</th>
            <th>Enforcement Status</th>
        </tr>
"@

foreach ($rule in $firewallRules) {
    $html += "<tr>
        <td>$($rule.Name)</td>
        <td>$($rule.DisplayName)</td>
        <td>$($rule.Description)</td>
        <td>$($rule.Direction)</td>
        <td>$($rule.Action)</td>
        <td>$($rule.EdgeTraversalPolicy)</td>
        <td>$($rule.Owner)</td>
        <td>$($rule.EnforcementStatus)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$outputPath = "$PWD\output\FirewallRulesReport.html"
$html | Out-File -Encoding utf8 -FilePath $outputPath