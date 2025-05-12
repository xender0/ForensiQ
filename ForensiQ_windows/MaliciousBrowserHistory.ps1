Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# --- GUI Setup ---
$form = New-Object System.Windows.Forms.Form
$form.Text = "Malicious URL Scanner"
$form.Size = New-Object System.Drawing.Size(900, 600)
$form.StartPosition = "CenterScreen"

# API Key Label and TextBox
$labelApiKey = New-Object System.Windows.Forms.Label
$labelApiKey.Text = "VirusTotal API Key:"
$labelApiKey.Location = New-Object System.Drawing.Point(10, 15)
$labelApiKey.Size = New-Object System.Drawing.Size(120, 20)
$form.Controls.Add($labelApiKey)

$textApiKey = New-Object System.Windows.Forms.TextBox
$textApiKey.Location = New-Object System.Drawing.Point(140, 10)
$textApiKey.Size = New-Object System.Drawing.Size(400, 20)
$form.Controls.Add($textApiKey)

# Fetch History Button
$btnFetch = New-Object System.Windows.Forms.Button
$btnFetch.Text = "Fetch Browser History"
$btnFetch.Location = New-Object System.Drawing.Point(560, 8)
$btnFetch.Size = New-Object System.Drawing.Size(150, 25)
$form.Controls.Add($btnFetch)

# ListView for URLs
$listView = New-Object System.Windows.Forms.ListView
$listView.Location = New-Object System.Drawing.Point(10, 50)
$listView.Size = New-Object System.Drawing.Size(860, 400)
$listView.View = 'Details'
$listView.CheckBoxes = $true
$listView.FullRowSelect = $true
$listView.Columns.Add("URL", 600)
$listView.Columns.Add("Browser", 100)
$listView.Columns.Add("Last Visited", 150)
$listView.Columns.Add("Result", 200)
$form.Controls.Add($listView)

# Check Selected URLs Button
$btnCheck = New-Object System.Windows.Forms.Button
$btnCheck.Text = "Check Selected URLs"
$btnCheck.Location = New-Object System.Drawing.Point(10, 470)
$btnCheck.Size = New-Object System.Drawing.Size(180, 30)
$form.Controls.Add($btnCheck)

# Results TextBox
$textResults = New-Object System.Windows.Forms.TextBox
$textResults.Location = New-Object System.Drawing.Point(10, 510)
$textResults.Size = New-Object System.Drawing.Size(860, 40)
$textResults.Multiline = $true
$textResults.ScrollBars = "Vertical"
$form.Controls.Add($textResults)

# --- Helper Functions ---

function Get-BrowserHistory {
    $results = @()
    # Chrome
    $chromePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\History"
    if (Test-Path $chromePath) {
        $temp = "$env:TEMP\chrome_history.db"
        Copy-Item $chromePath $temp -Force
        try {
            Import-Module PSSQLite -ErrorAction Stop
            $rows = Invoke-SqliteQuery -DataSource $temp -Query "SELECT url, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 1000;"
            foreach ($row in $rows) {
                $results += [PSCustomObject]@{
                    URL = $row.url
                    Browser = "Chrome"
                    LastVisited = $row.last_visit_time
                }
            }
        } catch {}
        Remove-Item $temp -ErrorAction SilentlyContinue
    }
    # Edge
    $edgePath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\History"
    if (Test-Path $edgePath) {
        $temp = "$env:TEMP\edge_history.db"
        Copy-Item $edgePath $temp -Force
        try {
            Import-Module PSSQLite -ErrorAction Stop
            $rows = Invoke-SqliteQuery -DataSource $temp -Query "SELECT url, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 1000;"
            foreach ($row in $rows) {
                $results += [PSCustomObject]@{
                    URL = $row.url
                    Browser = "Edge"
                    LastVisited = $row.last_visit_time
                }
            }
        } catch {}
        Remove-Item $temp -ErrorAction SilentlyContinue
    }
    # Firefox (first profile only for demo)
    $ffProfile = Get-ChildItem "$env:APPDATA\Mozilla\Firefox\Profiles\*\places.sqlite" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($ffProfile) {
        $temp = "$env:TEMP\firefox_history.db"
        Copy-Item $ffProfile.FullName $temp -Force
        try {
            Import-Module PSSQLite -ErrorAction Stop
            $rows = Invoke-SqliteQuery -DataSource $temp -Query "SELECT url, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT 1000;"
            foreach ($row in $rows) {
                $results += [PSCustomObject]@{
                    URL = $row.url
                    Browser = "Firefox"
                    LastVisited = $row.last_visit_date
                }
            }
        } catch {}
        Remove-Item $temp -ErrorAction SilentlyContinue
    }
    return $results | Where-Object { $_.URL -like "http*" }
}

function Get-UrlId ($Url) {
    $canonicalUrl = $Url.TrimEnd('/')
    $urlBytes = [System.Text.Encoding]::UTF8.GetBytes($canonicalUrl)
    $base64Url = [System.Convert]::ToBase64String($urlBytes)
    $urlId = $base64Url.Replace('+', '-').Replace('/', '_').TrimEnd('=')
    return $urlId
}

function Query-VirusTotalUrl ($Url, $ApiKey) {
    $urlId = Get-UrlId $Url
    $apiUrl = "https://www.virustotal.com/api/v3/urls/$urlId"
    $headers = @{ "x-apikey" = $ApiKey }
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method Get -ErrorAction Stop
        $malicious = $response.data.attributes.last_analysis_stats.malicious
        return @{ Malicious = $malicious; Error = $null }
    } catch {
        return @{ Malicious = $null; Error = $_.Exception.Message }
    }
}

# --- Button Events ---

$btnFetch.Add_Click({
    try {
        $listView.Items.Clear()
        $textResults.Text = "Fetching browser history..."
        $history = Get-BrowserHistory
        foreach ($entry in $history) {
            $item = New-Object System.Windows.Forms.ListViewItem($entry.URL)
            $item.SubItems.Add($entry.Browser)
            $item.SubItems.Add($entry.LastVisited)
            $item.SubItems.Add("") # Result column
            $listView.Items.Add($item)
        }
        $textResults.Text = "Fetched $($history.Count) URLs. Select which to check."
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Error fetching history: $($_.Exception.Message)")
    }
})

$btnCheck.Add_Click({
    try {
        $btnCheck.Enabled = $false
        $apiKey = $textApiKey.Text.Trim()
        if (-not $apiKey) {
            [System.Windows.Forms.MessageBox]::Show("Please enter your VirusTotal API key.")
            return
        }
        $selected = $listView.CheckedItems
        if ($selected.Count -eq 0) {
            [System.Windows.Forms.MessageBox]::Show("Please select at least one URL to check.")
            return
        }
        $textResults.Text = "Checking selected URLs (rate-limited, please wait)..."
        foreach ($item in $selected) {
            $url = $item.Text
            $result = Query-VirusTotalUrl $url $apiKey
            if ($result.Error) {
                $item.BackColor = [System.Drawing.Color]::Orange
                $item.SubItems[3].Text = "Error: $($result.Error)"
                $item.ToolTipText = $result.Error
            } elseif ($result.Malicious -gt 0) {
                $item.BackColor = [System.Drawing.Color]::Red
                $item.SubItems[3].Text = "Malicious: $($result.Malicious)"
            } else {
                $item.BackColor = [System.Drawing.Color]::LightGreen
                $item.SubItems[3].Text = "Clean"
            }
            Start-Sleep -Seconds 16 # VT free tier rate limit
        }
        $textResults.Text = "Check complete. Red = Malicious, Green = Clean, Orange = Error."
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Error: $($_.Exception.Message)")
    } finally {
        $btnCheck.Enabled = $true
    }
})

# --- Show Form ---
[void]$form.ShowDialog()
