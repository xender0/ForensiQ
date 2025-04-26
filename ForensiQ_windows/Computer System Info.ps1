$outputDir = "$PWD\output"
$outputFile = "$outputDir\SystemInfo.html"

if (!(Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

# --- Gather System Information with Error Handling ---
$ErrorActionPreference = "SilentlyContinue" # Prevent Get-WmiObject from stopping script on error

# Computer System
try {
    $systemInfo = Get-WmiObject -Class Win32_ComputerSystem -ErrorAction Stop | Select-Object Name, Caption, SystemType, Manufacturer, Model, DNSHostName, Domain, PartOfDomain, WorkGroup, CurrentTimeZone, PCSystemType, HyperVisorPresent
} catch {
    Write-Warning "Failed to get Win32_ComputerSystem info: $($_.Exception.Message)"
    $systemInfo = @{ Error = "Failed to retrieve Computer System info." }
}

# Operating System
try {
    $osInfo = Get-WmiObject -Class Win32_OperatingSystem -ErrorAction Stop | Select-Object Caption, Version, BuildNumber, InstallDate, LastBootUpTime, OSArchitecture
} catch {
    Write-Warning "Failed to get Win32_OperatingSystem info: $($_.Exception.Message)"
    $osInfo = @{ Error = "Failed to retrieve Operating System info." }
}

# Processor
try {
    $processorInfo = Get-WmiObject -Class Win32_Processor -ErrorAction Stop | Select-Object Name, NumberOfCores, MaxClockSpeed
} catch {
    Write-Warning "Failed to get Win32_Processor info: $($_.Exception.Message)"
    $processorInfo = @{ Error = "Failed to retrieve Processor info." }
}

# Memory (Convert Bytes to GB)
try {
    $memoryInfo = Get-WmiObject -Class Win32_PhysicalMemory -ErrorAction Stop | Measure-Object -Property Capacity -Sum
    $totalMemoryGB = [Math]::Round($memoryInfo.Sum / 1GB, 2)
} catch {
    Write-Warning "Failed to get Win32_PhysicalMemory info: $($_.Exception.Message)"
    $totalMemoryGB = "Error retrieving memory info."
}

# BIOS
try {
    $biosInfo = Get-WmiObject -Class Win32_BIOS -ErrorAction Stop | Select-Object Manufacturer, Version, SerialNumber
} catch {
    Write-Warning "Failed to get Win32_BIOS info: $($_.Exception.Message)"
    $biosInfo = @{ Error = "Failed to retrieve BIOS info." }
}

# TimeZone Name
$timeZoneName = "N/A" # Default value
if ($systemInfo -and -not $systemInfo.PSObject.Properties['Error']) {
    try {
        # Get the current time zone object based on the offset from Win32_ComputerSystem
        $currentTimeZoneObject = Get-WmiObject -Class Win32_TimeZone -ErrorAction Stop | Where-Object { $_.Bias -eq $systemInfo.CurrentTimeZone }
        if ($currentTimeZoneObject) {
            $timeZoneName = $currentTimeZoneObject.StandardName | Out-String -Stream # Get the name
        } else {
            $timeZoneName = "Unknown (Offset: $($systemInfo.CurrentTimeZone))"
        }
    } catch {
        Write-Warning "Failed to get Win32_TimeZone info: $($_.Exception.Message)"
        $timeZoneName = "Error retrieving TimeZone info."
    }
} elseif ($systemInfo) {
    # If systemInfo itself failed, we can't get timezone based on it
    $timeZoneName = "Error (depends on System Info)"
}


# --- Helper Functions/Logic for Formatting ---
# Function to safely get property value or return error message
Function Get-ValueOrDefault {
    param($object, $propertyName, [string]$default = "N/A")
    if ($object -and $object.PSObject.Properties[$propertyName]) {
        return $object.$propertyName
    } elseif ($object -and $object.PSObject.Properties['Error']) {
        # If the whole object failed to load, return its error message for the first property requested
        # For subsequent properties of the same failed object, return a simpler N/A
        if ($script:lastErrorObject -ne $object) {
             $script:lastErrorObject = $object
             return "<span style='color:red;'>$($object.Error)</span>"
        } else {
            return $default
        }
    }
    else {
        return $default
    }
}

# Function to convert WMI datetime to standard format (using Get-ValueOrDefault)
Function Convert-WMIFormattedDate {
    param($object, $propertyName)
    $wmiDate = Get-ValueOrDefault -object $object -propertyName $propertyName -default ""
    if ($wmiDate -is [string] -and $wmiDate -match '^\d{14}\.') {
        try {
            return [System.Management.ManagementDateTimeConverter]::ToDateTime($wmiDate).ToString("yyyy-MM-dd HH:mm:ss")
        } catch {
            return "$wmiDate (Conversion Error)" # Return original value with error note
        }
    } elseif ($wmiDate -like "*Error*") {
        return $wmiDate # Pass through existing error messages
    }
    else {
        return $wmiDate # Return original if not in expected format or empty
    }
}

# Function to convert boolean to Yes/No (using Get-ValueOrDefault)
Function Convert-BooleanToYesNo {
    param($object, $propertyName)
    $value = Get-ValueOrDefault -object $object -propertyName $propertyName -default $null
    if ($value -eq $true) { return "Yes" }
    elseif ($value -eq $false) { return "No" }
    elseif ($value -like "*Error*") { return $value } # Pass through error messages
    else { return "N/A" }
}

# Translate PCSystemType code (using Get-ValueOrDefault)
$pcSystemTypeCode = Get-ValueOrDefault -object $systemInfo -propertyName 'PCSystemType' -default -1
$pcSystemTypeDescription = switch ($pcSystemTypeCode) {
    0 { "Unspecified" }
    1 { "Desktop" }
    2 { "Mobile" }
    3 { "Workstation" }
    4 { "Enterprise Server" }
    5 { "SOHO Server" }
    6 { "Appliance PC" }
    7 { "Performance Server" }
    8 { "Maximum" } # Note: Values might vary slightly based on system/docs
    -1 { Get-ValueOrDefault -object $systemInfo -propertyName 'PCSystemType' } # Handles error case from Get-ValueOrDefault
    default { "Unknown ($pcSystemTypeCode)" }
}

# Clear last error object tracker before generating HTML
$script:lastErrorObject = $null

# --- Generate HTML Table Content ---
# Note: We now call the helper functions directly within the HTML string for cleaner code
$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>System Information</title>
    <!-- Basic Styling (Optional, as index.html applies Bootstrap) -->
    <style>
        /* Minimal styles if viewed directly */
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>System Information</h2>
    <table class="table table-striped table-bordered table-hover"> <!-- Added Bootstrap classes -->
        <thead>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            <!-- Computer System Info -->
            <tr><td>Computer Name</td><td>$(Get-ValueOrDefault $systemInfo 'Name')</td></tr>
            <tr><td>System Manufacturer</td><td>$(Get-ValueOrDefault $systemInfo 'Manufacturer')</td></tr>
            <tr><td>System Model</td><td>$(Get-ValueOrDefault $systemInfo 'Model')</td></tr>
            <tr><td>System Type</td><td>$(Get-ValueOrDefault $systemInfo 'SystemType')</td></tr>
            <tr><td>DNS Host Name</td><td>$(Get-ValueOrDefault $systemInfo 'DNSHostName')</td></tr>
            <tr><td>Domain</td><td>$(Get-ValueOrDefault $systemInfo 'Domain')</td></tr>
            <tr><td>Part of Domain</td><td>$(Convert-BooleanToYesNo $systemInfo 'PartOfDomain')</td></tr>
            <tr><td>WorkGroup</td><td>$(Get-ValueOrDefault $systemInfo 'WorkGroup')</td></tr>
            <tr><td>PC System Type</td><td>$($pcSystemTypeDescription)</td></tr>
            <tr><td>HyperVisor Present</td><td>$(Convert-BooleanToYesNo $systemInfo 'HyperVisorPresent')</td></tr>
            <tr><td>Current Time Zone</td><td>$($timeZoneName)</td></tr>
            <!-- OS Info -->
            <tr><td>OS Name</td><td>$(Get-ValueOrDefault $osInfo 'Caption')</td></tr>
            <tr><td>OS Version</td><td>$(Get-ValueOrDefault $osInfo 'Version')</td></tr>
            <tr><td>OS Build</td><td>$(Get-ValueOrDefault $osInfo 'BuildNumber')</td></tr>
            <tr><td>OS Architecture</td><td>$(Get-ValueOrDefault $osInfo 'OSArchitecture')</td></tr>
            <tr><td>OS Install Date</td><td>$(Convert-WMIFormattedDate $osInfo 'InstallDate')</td></tr>
            <tr><td>Last Boot Time</td><td>$(Convert-WMIFormattedDate $osInfo 'LastBootUpTime')</td></tr>
            <!-- Processor Info -->
            <tr><td>Processor</td><td>$(Get-ValueOrDefault $processorInfo 'Name')</td></tr>
            <tr><td>Processor Cores</td><td>$(Get-ValueOrDefault $processorInfo 'NumberOfCores')</td></tr>
            <tr><td>Processor Max Speed (MHz)</td><td>$(Get-ValueOrDefault $processorInfo 'MaxClockSpeed')</td></tr>
            <!-- Memory Info -->
            <tr><td>Total Physical Memory (GB)</td><td>$($totalMemoryGB)</td></tr> <!-- Already handles error -->
            <!-- BIOS Info -->
            <tr><td>BIOS Manufacturer</td><td>$(Get-ValueOrDefault $biosInfo 'Manufacturer')</td></tr>
            <tr><td>BIOS Version</td><td>$(Get-ValueOrDefault $biosInfo 'Version')</td></tr>
            <tr><td>BIOS Serial Number</td><td>$(Get-ValueOrDefault $biosInfo 'SerialNumber')</td></tr>
        </tbody>
    </table>
</body>
</html>
"@

$htmlContent | Out-File -Encoding UTF8 -FilePath $outputFile

Write-Output "Results saved to: $outputFile"
