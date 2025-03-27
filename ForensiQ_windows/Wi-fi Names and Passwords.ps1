$wifiProfiles = netsh.exe wlan show profiles | Select-String "\:(.+)$" | ForEach-Object { 
    $wlanname = $_.Matches.Groups[1].Value.Trim(); 
    (netsh wlan show profile name="$wlanname" key=clear) | Select-String 'Key Content\W+\:(.+)$' | ForEach-Object { 
        $wlanpass = $_.Matches.Groups[1].Value.Trim(); 
        [PSCustomObject]@{ PROFILE_NAME = $wlanname; PASSWORD = $wlanpass } 
    } 
}

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Wi-Fi Passwords</title>
</head>
<body>
    <h2>Wi-Fi Profiles and Passwords</h2>
    <table border="1">
        <tr>
            <th>Profile Name</th>
            <th>Password</th>
        </tr>
"@

foreach ($profile in $wifiProfiles) {
    $html += @"
        <tr>
            <td>$($profile.PROFILE_NAME)</td>
            <td>$($profile.PASSWORD)</td>
        </tr>
"@
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\WiFiPasswords.html"
$html | Out-File -Encoding utf8 -FilePath $path