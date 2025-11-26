from typing import Dict, List
from datetime import datetime
from pathlib import Path
import json


def generate_html_report(output_data: Dict, output_path: Path) -> str:
    html_content = generate_html_content(output_data)
    
    html_file = output_path.parent / "forensics_report.html"
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(html_file)


def generate_html_content(output_data: Dict) -> str:
    timestamp = output_data.get('collection_timestamp', datetime.now().isoformat())
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ForensiQ (Android) Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .summary-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-header {{
            background: #667eea;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .section-header h2 {{
            font-size: 1.5em;
        }}
        
        .count-badge {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        thead {{
            background: #667eea;
            color: white;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tbody tr:hover {{
            background: #f5f5f5;
        }}
        
        tbody tr:nth-child(even) {{
            background: #fafafa;
        }}
        
        .type-incoming {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .type-outgoing {{
            color: #007bff;
            font-weight: bold;
        }}
        
        .type-missed {{
            color: #dc3545;
            font-weight: bold;
        }}
        
        .sms-inbox {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .sms-sent {{
            color: #007bff;
            font-weight: bold;
        }}
        
        .read-status {{
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
        }}
        
        .read {{
            background: #d4edda;
            color: #155724;
        }}
        
        .unread {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }}
        
        .json-section {{
            background: #f8f9fa;
            border-radius: 5px;
            padding: 20px;
            margin-top: 20px;
        }}
        
        .json-section pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.9em;
            line-height: 1.5;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 ForensiQ (Android) Report</h1>
            <p>Generated on {format_timestamp(timestamp)}</p>
        </div>
        
        <div class="content">
            <!-- Summary Section -->
            <div class="summary">
                <div class="summary-card">
                    <h3>Contacts</h3>
                    <div class="value">{len(output_data.get('contacts', []))}</div>
                </div>
                <div class="summary-card">
                    <h3>SMS Messages</h3>
                    <div class="value">{len(output_data.get('sms', []))}</div>
                </div>
                <div class="summary-card">
                    <h3>Call Logs</h3>
                    <div class="value">{len(output_data.get('call_logs', []))}</div>
                </div>
                <div class="summary-card">
                    <h3>Installed Apps</h3>
                    <div class="value">{len(output_data.get('installed_apps', []))}</div>
                </div>
            </div>
            
            <!-- Contacts Section -->
            {generate_contacts_section(output_data.get('contacts', []))}
            
            <!-- SMS Section -->
            {generate_sms_section(output_data.get('sms', []))}
            
            <!-- Call Logs Section -->
            {generate_call_logs_section(output_data.get('call_logs', []))}
            
            <!-- Device Info Section -->
            {generate_device_info_section(output_data.get('device_info', {}))}
        </div>
        
        <div class="footer">
            <p>Report generated by ForensiQ (Android) | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def format_timestamp(timestamp: str) -> str:
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp


def generate_contacts_section(contacts: List[Dict]) -> str:
    if not contacts:
        return """
            <div class="section">
                <div class="section-header">
                    <h2>📇 Contacts</h2>
                    <span class="count-badge">0 contacts</span>
                </div>
                <div class="no-data">No contacts found or access denied.</div>
            </div>
        """
    
    html = f"""
        <div class="section">
            <div class="section-header">
                <h2>📇 Contacts</h2>
                <span class="count-badge">{len(contacts)} contacts</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Phone Number</th>
                        <th>Type</th>
                        <th>Contact ID</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for contact in contacts:
        html += f"""
                    <tr>
                        <td>{escape_html(str(contact.get('_id', 'N/A')))}</td>
                        <td>{escape_html(str(contact.get('display_name', 'N/A')))}</td>
                        <td>{escape_html(str(contact.get('phone_number', 'N/A')))}</td>
                        <td>{escape_html(str(contact.get('phone_type', 'N/A')))}</td>
                        <td>{escape_html(str(contact.get('contact_id', 'N/A')))}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    """
    
    return html


def generate_sms_section(sms_list: List[Dict]) -> str:
    if not sms_list:
        return """
            <div class="section">
                <div class="section-header">
                    <h2>💬 SMS Messages</h2>
                    <span class="count-badge">0 messages</span>
                </div>
                <div class="no-data">No SMS messages found or access denied.</div>
            </div>
        """
    
    inbox_count = sum(1 for s in sms_list if s.get('type_code') == '1')
    sent_count = sum(1 for s in sms_list if s.get('type_code') == '2')
    
    html = f"""
        <div class="section">
            <div class="section-header">
                <h2>💬 SMS Messages</h2>
                <span class="count-badge">{len(sms_list)} messages (Inbox: {inbox_count}, Sent: {sent_count})</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Address</th>
                        <th>Type</th>
                        <th>Read</th>
                        <th>Date</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for sms in sms_list:
        sms_type = sms.get('type', 'N/A')
        type_class = 'sms-inbox' if sms.get('type_code') == '1' else 'sms-sent' if sms.get('type_code') == '2' else ''
        read_status = sms.get('read', 'N/A')
        read_class = 'read' if read_status == 'Read' else 'unread'
        body = str(sms.get('body', 'N/A'))
        if len(body) > 100:
            body = body[:97] + "..."
        
        html += f"""
                    <tr>
                        <td>{escape_html(str(sms.get('_id', 'N/A')))}</td>
                        <td>{escape_html(str(sms.get('address', 'N/A')))}</td>
                        <td class="{type_class}">{escape_html(sms_type)}</td>
                        <td><span class="read-status {read_class}">{escape_html(read_status)}</span></td>
                        <td>{escape_html(str(sms.get('date', 'N/A')))}</td>
                        <td>{escape_html(body)}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    """
    
    return html


def generate_call_logs_section(call_logs: List[Dict]) -> str:
    if not call_logs:
        return """
            <div class="section">
                <div class="section-header">
                    <h2>📞 Call Logs</h2>
                    <span class="count-badge">0 calls</span>
                </div>
                <div class="no-data">No call logs found or access denied.</div>
            </div>
        """
    
    incoming_count = sum(1 for c in call_logs if c.get('type_code') == '1')
    outgoing_count = sum(1 for c in call_logs if c.get('type_code') == '2')
    missed_count = sum(1 for c in call_logs if c.get('type_code') == '3')
    
    html = f"""
        <div class="section">
            <div class="section-header">
                <h2>📞 Call Logs</h2>
                <span class="count-badge">{len(call_logs)} calls (Incoming: {incoming_count}, Outgoing: {outgoing_count}, Missed: {missed_count})</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Number</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Date</th>
                        <th>Duration</th>
                        <th>Location</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for call in call_logs:
        name = call.get('name', 'N/A')
        if name == 'N/A' and call.get('cached_name') != 'N/A':
            name = call.get('cached_name', 'N/A')
        
        call_type = call.get('type', 'N/A')
        type_code = call.get('type_code', '0')
        type_class = ''
        if type_code == '1':
            type_class = 'type-incoming'
        elif type_code == '2':
            type_class = 'type-outgoing'
        elif type_code == '3':
            type_class = 'type-missed'
        
        html += f"""
                    <tr>
                        <td>{escape_html(str(call.get('_id', 'N/A')))}</td>
                        <td>{escape_html(str(call.get('number', 'N/A')))}</td>
                        <td>{escape_html(str(name))}</td>
                        <td class="{type_class}">{escape_html(call_type)}</td>
                        <td>{escape_html(str(call.get('date', 'N/A')))}</td>
                        <td>{escape_html(str(call.get('duration', 'N/A')))}</td>
                        <td>{escape_html(str(call.get('geocoded_location', 'N/A')))}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    """
    
    return html


def generate_device_info_section(device_info: Dict) -> str:
    if not device_info:
        return ""
    
    html = """
        <div class="section">
            <div class="section-header">
                <h2>📱 Device Information</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    key_fields = [
        ('model', 'Model'),
        ('manufacturer', 'Manufacturer'),
        ('brand', 'Brand'),
        ('android_version', 'Android Version'),
        ('sdk_version', 'SDK Version'),
        ('serial', 'Serial Number'),
        ('android_id', 'Android ID'),
        ('hardware', 'Hardware'),
        ('cpu_abi', 'CPU ABI'),
        ('security_patch', 'Security Patch Level'),
        ('boot_time', 'Boot Time'),
    ]
    
    for key, label in key_fields:
        value = device_info.get(key, 'N/A')
        html += f"""
                    <tr>
                        <td><strong>{label}</strong></td>
                        <td>{escape_html(str(value))}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    """
    
    return html


def escape_html(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;'))

