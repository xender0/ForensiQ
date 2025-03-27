$installedProducts = Get-CimInstance -ClassName win32_product | 
    Select-Object Name, Version, Vendor, InstallDate, InstallSource, PackageName, LocalPackage

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Installed Products Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Installed Products Report</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Version</th>
            <th>Vendor</th>
            <th>Install Date</th>
            <th>Install Source</th>
            <th>Package Name</th>
            <th>Local Package</th>
        </tr>
"@

foreach ($product in $installedProducts) {
    $html += "<tr>
        <td>$($product.Name)</td>
        <td>$($product.Version)</td>
        <td>$($product.Vendor)</td>
        <td>$($product.InstallDate)</td>
        <td>$($product.InstallSource)</td>
        <td>$($product.PackageName)</td>
        <td>$($product.LocalPackage)</td>
    </tr>"
}

$html += @"
    </table>
</body>
</html>
"@

$path = "$PWD\output\InstalledProductsReport.html"
$html | Out-File -Encoding utf8 -FilePath $path
