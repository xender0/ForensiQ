import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import subprocess
import threading
import os
import sys
import tempfile
import shutil

# --- PowerShell Script Content (Embedded) ---
POWERSHELL_SCRIPT_CONTENT = r'''
#Requires -Modules PSSQLite
#Requires -RunAsAdministrator
param(
    [Parameter(Mandatory=$true)]
    [string]$VirusTotalApiKey,

    [Parameter(Mandatory=$false)]
    [string]$BrowsersToScan
)

# Split and trim browser list if provided
if ($BrowsersToScan) {
    $BrowsersToScan = $BrowsersToScan -split ',' | ForEach-Object { $_.Trim() }
    Write-Host "Scanning browsers: $($BrowsersToScan -join ', ')"
}

# --- Configuration ---
$OutputDirectory = Join-Path $PSScriptRoot "output"
$OutputFileName = "Malicious_URL_Scan_Report.html"
$RateLimitSleepSeconds = 15
$TempDbPath = Join-Path $env:TEMP "HistoryScanTempDB"

# --- Function Definitions ---
Function Test-AndInstall-PSSQLite {
    if (-not (Get-Module -ListAvailable -Name PSSQLite)) {
        Write-Host "PSSQLite module not found. Attempting to install..."
        try {
            Install-Module PSSQLite -Force -SkipPublisherCheck -Scope CurrentUser -ErrorAction Stop
            Write-Host "PSSQLite installed successfully." -ForegroundColor Green
            Import-Module PSSQLite -ErrorAction Stop
        } catch {
            Write-Error "Failed to install PSSQLite. Please install it manually: Install-Module PSSQLite -Scope CurrentUser"
            return $false
        }
    } elseif (-not (Get-Module -Name PSSQLite)) {
        try {
            Import-Module PSSQLite -ErrorAction Stop
            Write-Host "PSSQLite module imported."
        } catch {
            Write-Error "Failed to import PSSQLite: $($_.Exception.Message)"
            return $false
        }
    }
    return $true
}

Function Get-UrlId {
    param([string]$Url)
    $canonicalUrl = $Url.TrimEnd('/')
    $urlBytes = [System.Text.Encoding]::UTF8.GetBytes($canonicalUrl)
    $base64Url = [System.Convert]::ToBase64String($urlBytes)
    return $base64Url.Replace('+', '-').Replace('/', '_').TrimEnd('=')
}

Function Query-VirusTotalUrl {
    param(
        [string]$Url,
        [string]$ApiKey,
        [hashtable]$ProcessedUrlsCache
    )
    if ($ProcessedUrlsCache.ContainsKey($Url)) {
        Write-Verbose "URL already processed (cached): $Url"
        return $ProcessedUrlsCache[$Url]
    }
    $urlId = Get-UrlId -Url $Url
    $apiUrl = "https://www.virustotal.com/api/v3/urls/$urlId"
    $headers = @{ "x-apikey" = $ApiKey }
    Write-Verbose "Querying VT for URL: $Url (ID: $urlId)"
    try {
        Start-Sleep -Seconds $RateLimitSleepSeconds
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method Get -ErrorAction Stop
        $maliciousCount = $response.data.attributes.last_analysis_stats.malicious
        $totalEngines = ($response.data.attributes.last_analysis_stats.malicious + 
                         $response.data.attributes.last_analysis_stats.suspicious + 
                         $response.data.attributes.last_analysis_stats.harmless + 
                         $response.data.attributes.last_analysis_stats.undetected)
        if ($totalEngines -eq 0) {
            $totalEngines = $response.data.attributes.last_analysis_stats | 
                           Get-Member -MemberType NoteProperty | 
                           Where-Object {$_.Name -ne "timeout"} | 
                           Measure-Object | 
                           Select-Object -ExpandProperty Count
        }
        $vtLink = "https://www.virustotal.com/gui/url/$urlId"
        $result = [PSCustomObject]@{
            Url = $Url
            MaliciousHits = $maliciousCount
            TotalEngines = $totalEngines
            VirusTotalLink = $vtLink
            Status = 'Checked'
            Error = $null
        }
        $ProcessedUrlsCache[$Url] = $result
        return $result
    } catch {
        $statusCode = 0
        if ($_.Exception.Response) { $statusCode = $_.Exception.Response.StatusCode.Value__ }
        $errorMessage = $_.Exception.Message
        Write-Warning "Error querying VT for '$Url' (HTTP $statusCode): $errorMessage"
        $result = [PSCustomObject]@{
            Url = $Url
            MaliciousHits = $null
            TotalEngines = $null
            VirusTotalLink = $null
            Status = 'Error'
            Error = "HTTP $statusCode: $errorMessage"
        }
        $ProcessedUrlsCache[$Url] = $result
        return $result
    }
}

# --- Main Script Logic ---
Write-Host "Malicious URL Scanner Started..."

# 1. Check Dependencies
Write-Host "Checking dependencies..."
if (-not (Test-AndInstall-PSSQLite)) {
    Write-Error "PSSQLite module is required and could not be installed. Exiting."
    Exit 1
}

# 2. Prepare Output and Temp Directories
Write-Host "Preparing directories..."
if (-not (Test-Path $OutputDirectory)) {
    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
}
if (Test-Path $TempDbPath) {
    Remove-Item -Recurse -Force $TempDbPath
}
New-Item -ItemType Directory -Path $TempDbPath -Force | Out-Null

# 3. Define Browser Queries
$allBrowserData = @(
    @{ 
        Name = "Chrome"
        Query = "SELECT url, last_visit_time FROM urls ORDER BY last_visit_time DESC;"
    },
    @{ 
        Name = "Edge"
        Query = "SELECT url, last_visit_time FROM urls ORDER BY last_visit_time DESC;"
    },
    @{ 
        Name = "Firefox"
        Query = "SELECT url, last_visit_date FROM moz_places ORDER BY last_visit_date DESC;"
    }
)

$selectedBrowserData = $allBrowserData
if ($PSBoundParameters.ContainsKey('BrowsersToScan') -and $BrowsersToScan -and ($BrowsersToScan.Count -gt 0)) {
    Write-Host "Filtering browsers to scan: $($BrowsersToScan -join ', ')"
    $selectedBrowserData = $allBrowserData | Where-Object { $BrowsersToScan -contains $_.Name }
} else {
    Write-Host "No specific browsers selected. Scanning all supported browsers."
}

if ($selectedBrowserData.Count -eq 0) {
    Write-Warning "No valid browsers specified. Will scan all supported browsers."
    $selectedBrowserData = $allBrowserData
}

$allUrls = @{}
$maliciousResults = @()
$processedUrlsCache = @{}

# 4. Extract URLs from Selected Browsers
Write-Host "Extracting URLs from browser history..."
foreach ($browser in $selectedBrowserData) {
    Write-Host "Checking $($browser.Name)..."
    $historyFiles = @()
    
    if ($browser.Name -eq "Firefox") {
        $firefoxProfilesPath = Join-Path $env:APPDATA "Mozilla\Firefox\Profiles"
        if (Test-Path $firefoxProfilesPath) {
            $historyFiles = Get-ChildItem -Path (Join-Path $firefoxProfilesPath "*\places.sqlite") -File -ErrorAction SilentlyContinue
        }
    } else {
        $userDataPath = ""
        if ($browser.Name -eq "Chrome") {
            $userDataPath = Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data"
        } elseif ($browser.Name -eq "Edge") {
            $userDataPath = Join-Path $env:LOCALAPPDATA "Microsoft\Edge\User Data"
        }
        
        if (Test-Path $userDataPath) {
            $historyFiles = Get-ChildItem -Path (Join-Path $userDataPath "*\History") -File -ErrorAction SilentlyContinue
        }
    }

    if (-not $historyFiles -or $historyFiles.Count -eq 0) {
        Write-Warning "$($browser.Name) history file(s) not found."
        continue
    }

    foreach ($historyFile in $historyFiles) {
        $profileName = Split-Path -Parent $historyFile.FullName | Split-Path -Leaf
        $tempHistoryFile = Join-Path $TempDbPath "$($browser.Name)_${profileName}_History.db"
        try {
            Copy-Item -Path $historyFile.FullName -Destination $tempHistoryFile -Force -ErrorAction Stop
            Write-Verbose "Copied $($browser.Name) history to $tempHistoryFile"
        } catch {
            Write-Warning "Failed to copy $($browser.Name) history file. It might be in use. Skipping."
            continue
        }

        try {
            $urls = Invoke-SqliteQuery -DataSource $tempHistoryFile -Query $browser.Query -ErrorAction Stop
            Write-Host " Found $($urls.Count) URLs in $($browser.Name) profile '$profileName'."
            foreach ($entry in $urls) {
                $url = $entry.url
                if (-not [string]::IsNullOrWhiteSpace($url) -and $url -like 'http*') {
                    if (-not $allUrls.ContainsKey($url)) {
                        $allUrls[$url] = "$($browser.Name) ($profileName)"
                    }
                }
            }
        } catch {
            Write-Warning "Failed to query $($browser.Name) history database: $($_.Exception.Message)"
        }
    }
}

# 5. Check URLs against VirusTotal
$totalUniqueUrls = $allUrls.Keys.Count
if ($totalUniqueUrls -eq 0) {
    Write-Host "No URLs found in browser histories."
} else {
    Write-Host "Found $totalUniqueUrls unique URLs to check against VirusTotal..."
    $i = 0
    foreach ($url in $allUrls.Keys) {
        $i++
        Write-Host "($i/$totalUniqueUrls) Checking URL: $url"
        $vtResult = Query-VirusTotalUrl -Url $url -ApiKey $VirusTotalApiKey -ProcessedUrlsCache $processedUrlsCache
        Write-Host " -> Hits: $($vtResult.MaliciousHits)/$($vtResult.TotalEngines). Status: $($vtResult.Status)"

        if ($vtResult -ne $null -and $vtResult.Status -eq 'Checked' -and $vtResult.MaliciousHits -gt 0) {
            $maliciousResults += [PSCustomObject]@{
                URL = $vtResult.Url
                BrowserSource = $allUrls[$url]
                MaliciousHits = $vtResult.MaliciousHits
                TotalEngines = $vtResult.TotalEngines
                VirusTotalLink = $vtResult.VirusTotalLink
            }
        } elseif ($vtResult -ne $null -and $vtResult.Status -eq 'Error') {
            Write-Warning "Failed to get VT result for $url : $($vtResult.Error)"
        }
    }
}

# 6. Generate HTML Report
Write-Host "Generating HTML report..."
$reportPath = Join-Path $OutputDirectory $OutputFileName
$htmlHeader = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Malicious URL Scan Report</title>
    <style>
        body {font-family: Arial, sans-serif; margin: 20px; line-height: 1.6;}
        h1, h2 {color: #2c3e50;}
        table {border-collapse: collapse; width: 100%; margin: 20px 0;}
        th, td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        th {background-color: #f2f2f2; font-weight: bold;}
        tr:nth-child(even) {background-color: #f9f9f9;}
        tr:hover {background-color: #e2e2e2;}
        .malicious {color: #e74c3c; font-weight: bold;}
        a {color: #3498db; text-decoration: none;}
        a:hover {text-decoration: underline;}
        .summary {margin: 20px 0; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #2c3e50;}
    </style>
</head>
<body>
    <h1>Malicious URL Scan Report</h1>
    <div class="summary">
        <p><strong>Scan Date:</strong> $(Get-Date)</p>
        <p><strong>Browsers Scanned:</strong> $($selectedBrowserData.Name -join ', ')</p>
        <p><strong>Total URLs Scanned:</strong> $totalUniqueUrls</p>
        <p><strong>Malicious URLs Found:</strong> $($maliciousResults.Count)</p>
    </div>
"@

$htmlFooter = "</body></html>"

$htmlBody = ""
if ($maliciousResults.Count -gt 0) {
    $htmlBody += "<h2>Malicious URLs</h2>"
    $htmlBody += "<p>The following URLs from browser history were flagged as malicious by VirusTotal:</p>"
    $htmlTable = $maliciousResults | 
                 Select-Object URL, BrowserSource, 
                 @{Name='Detections';Expression={$_.MaliciousHits}}, 
                 @{Name='Total Engines';Expression={$_.TotalEngines}}, 
                 @{Name='VirusTotal Report';Expression={"<a href='$($_.VirusTotalLink)' target='_blank'>View Report</a>"}} |
                 ConvertTo-Html -Fragment
    $htmlBody += $htmlTable
} else {
    $htmlBody += "<h2>No Malicious URLs Found</h2>"
    $htmlBody += "<p>No malicious URLs were detected among the $totalUniqueUrls URLs scanned from browser history.</p>"
}

$htmlContent = $htmlHeader + $htmlBody + $htmlFooter
try {
    $htmlContent | Out-File -FilePath $reportPath -Encoding UTF8 -ErrorAction Stop
    Write-Host "HTML report saved to '$reportPath'" -ForegroundColor Green
} catch {
    Write-Error "Failed to save HTML report: $($_.Exception.Message)"
}

# 7. Cleanup Temp Files
Write-Host "Cleaning up temporary files..."
if (Test-Path $TempDbPath) {
    Remove-Item -Recurse -Force $TempDbPath -ErrorAction SilentlyContinue
}

Write-Host "Scan completed."
'''

class BrowserURLScannerGUI:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Browser URL Scanner - VirusTotal")
        self.root.geometry("800x600")
        
        # --- Variables ---
        self.api_key_var = tk.StringVar()
        self.chrome_var = tk.BooleanVar(value=True)
        self.edge_var = tk.BooleanVar(value=True)
        self.firefox_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready. Enter your VirusTotal API key and select browsers to scan.")
        
        # --- Create UI ---
        self.create_widgets()
    
    def create_widgets(self):
        # API Key Frame
        api_frame = ttkb.LabelFrame(self.root, text="VirusTotal API Key", padding=10)
        api_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT, padx=5)
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=60, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Browser Selection Frame
        browser_frame = ttkb.LabelFrame(self.root, text="Select Browsers to Scan", padding=10)
        browser_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.chrome_check = ttkb.Checkbutton(browser_frame, text="Google Chrome", 
                                            variable=self.chrome_var, 
                                            bootstyle="primary-round-toggle")
        self.chrome_check.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.edge_check = ttkb.Checkbutton(browser_frame, text="Microsoft Edge", 
                                          variable=self.edge_var, 
                                          bootstyle="primary-round-toggle")
        self.edge_check.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.firefox_check = ttkb.Checkbutton(browser_frame, text="Mozilla Firefox", 
                                             variable=self.firefox_var, 
                                             bootstyle="primary-round-toggle")
        self.firefox_check.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Action Buttons Frame
        action_frame = ttkb.Frame(self.root, padding=10)
        action_frame.pack(fill=tk.X)
        
        self.scan_button = ttkb.Button(action_frame, text="Start URL Scan", 
                                      command=self.start_scan,
                                      bootstyle="success")
        self.scan_button.pack(pady=5)
        
        # Output Frame
        output_frame = ttkb.LabelFrame(self.root, text="Scan Progress", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80, 
                                                   wrap=tk.WORD, state=tk.DISABLED,
                                                   font=("Consolas", 9))
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Status Bar
        status_frame = ttkb.Frame(self.root, padding=(10, 5))
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttkb.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_bar = ttkb.Progressbar(status_frame, mode='indeterminate', length=150)
    
    def update_output(self, message, clear_first=False):
        self.output_text.config(state=tk.NORMAL)
        if clear_first:
            self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def start_scan(self):
        # Validate API key
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your VirusTotal API Key")
            return
        
        # Check if any browser is selected
        if not (self.chrome_var.get() or self.edge_var.get() or self.firefox_var.get()):
            messagebox.showerror("Error", "Please select at least one browser to scan")
            return
        
        # Disable UI during scan
        self.scan_button.config(state=tk.DISABLED)
        self.status_var.set("Scan in progress... This will take some time due to VirusTotal rate limits.")
        
        # Show progress bar
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.progress_bar.start(10)
        
        # Clear output and show initial message
        self.update_output("Starting browser history scan...", clear_first=True)
        self.update_output(f"API Key: {'*' * len(api_key[:-4]) + api_key[-4:]}")
        
        # Collect selected browsers
        selected_browsers = []
        if self.chrome_var.get(): selected_browsers.append("Chrome")
        if self.edge_var.get(): selected_browsers.append("Edge")
        if self.firefox_var.get(): selected_browsers.append("Firefox")
        
        self.update_output(f"Selected browsers: {', '.join(selected_browsers)}")
        
        # Start scan in a separate thread
        scan_thread = threading.Thread(target=self.run_scan,
                                      args=(api_key, selected_browsers),
                                      daemon=True)
        scan_thread.start()
    
    def run_scan(self, api_key, selected_browsers):
        temp_script_path = None
        report_path = None
        
        try:
            # Create temp dir for output
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Create temp script file
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ps1", encoding="utf-8") as tmp:
                tmp.write(POWERSHELL_SCRIPT_CONTENT)
                temp_script_path = tmp.name
            
            self.root.after(0, self.update_output, f"Created temporary script: {temp_script_path}")
            
            # Build PowerShell command
            ps_command = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", temp_script_path,
                "-VirusTotalApiKey", api_key
            ]
            
            # Add browser parameter if specified
            if selected_browsers:
                ps_command.extend(["-BrowsersToScan", ",".join(selected_browsers)])
            
            # Run PowerShell script
            self.root.after(0, self.update_output, "Executing PowerShell script...")
            
            process = subprocess.Popen(
                ps_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Process output in real-time
            for line in iter(process.stdout.readline, ''):
                if not line.strip():
                    continue
                self.root.after(0, self.update_output, line.strip())
            
            # Process any errors
            for line in iter(process.stderr.readline, ''):
                if not line.strip():
                    continue
                self.root.after(0, self.update_output, f"ERROR: {line.strip()}")
            
            # Wait for process to complete
            return_code = process.wait()
            
            # Look for the report
            report_path = os.path.join(output_dir, "Malicious_URL_Scan_Report.html")
            
            if return_code == 0:
                if os.path.exists(report_path):
                    self.root.after(0, self.update_output, f"Scan completed successfully. Report saved at: {report_path}")
                    self.root.after(0, self.status_var.set, "Scan completed. Opening report...")
                    
                    # Open the report
                    try:
                        os.startfile(report_path)
                    except Exception as e:
                        self.root.after(0, self.update_output, f"Could not open report: {e}")
                else:
                    self.root.after(0, self.update_output, "Scan completed but report file not found")
                    self.root.after(0, self.status_var.set, "Scan completed but report file not found")
            else:
                self.root.after(0, self.update_output, f"Scan failed with return code {return_code}")
                self.root.after(0, self.status_var.set, f"Scan failed with return code {return_code}")
                
        except Exception as e:
            self.root.after(0, self.update_output, f"Error running scan: {str(e)}")
            self.root.after(0, self.status_var.set, "Error running scan")
            import traceback
            self.root.after(0, self.update_output, traceback.format_exc())
            
        finally:
            # Clean up
            if temp_script_path and os.path.exists(temp_script_path):
                try:
                    os.remove(temp_script_path)
                    self.root.after(0, self.update_output, "Temporary script removed")
                except Exception as e:
                    self.root.after(0, self.update_output, f"Failed to remove temporary script: {e}")
            
            # Re-enable UI
            self.root.after(0, self.scan_button.config, {"state": tk.NORMAL})
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, self.progress_bar.pack_forget)

if __name__ == "__main__":
    # Check for admin privileges
    is_admin = False
    if sys.platform == "win32":
        try:
            is_admin = (os.getuid() == 0)
        except AttributeError:
            try:
                subprocess.check_output("net session", stderr=subprocess.STDOUT, shell=True, timeout=2)
                is_admin = True
            except:
                is_admin = False
    
    app_root = ttkb.Window(themename="darkly")
    app = BrowserURLScannerGUI(app_root)
    
    if sys.platform == "win32" and not is_admin:
        messagebox.showwarning("Administrator Required", 
                              "This tool requires administrator privileges to access browser history files "
                              "and install the required PowerShell module.\n\n"
                              "Please run the application as administrator.")
    
    app_root.mainloop()
