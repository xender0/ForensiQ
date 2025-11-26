from typing import List, Dict
from ..utils import run_adb_command, parse_date
import re


def extract_call_logs() -> List[Dict]:
    call_logs = []
    output = run_adb_command('shell content query --uri content://call_log/calls')
    if not output:
        return call_logs
    lines = output.split('\n')
    current_row = None
    current_row_data = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('Row:'):
            if current_row is not None:
                try:
                    call_data = parse_content_query_row(current_row_data)
                    if call_data:
                        call_logs.append(create_call_entry(call_data))
                except:
                    pass
            current_row = line
            current_row_data = [line]
        elif current_row is not None:
            current_row_data.append(line)
    if current_row is not None:
        try:
            call_data = parse_content_query_row(current_row_data)
            if call_data:
                call_logs.append(create_call_entry(call_data))
        except:
            pass
    return call_logs


def parse_content_query_row(row_lines):
    full_text = ' '.join(row_lines)
    data_part = re.sub(r'^Row: \d+ ', '', full_text)
    parts = re.split(r',\s*(?=\w+=)', data_part)
    call_data = {}
    for part in parts:
        if '=' in part:
            key_value = part.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if value == 'NULL' or value == '':
                    value = 'N/A'
                else:
                    value = value.strip("'\"")
                call_data[key] = value
    return call_data


def create_call_entry(call_data):
    date_str = call_data.get('date', '0')
    formatted_date = parse_date(date_str) if date_str and date_str.isdigit() else 'N/A'
    duration_str = call_data.get('duration', '0')
    try:
        duration_seconds = int(duration_str) if duration_str and duration_str.isdigit() else 0
        duration_formatted = f"{duration_seconds // 60}:{duration_seconds % 60:02d}"
    except:
        duration_formatted = '0:00'
    call_type = str(call_data.get('type', '0'))
    type_map = {
        '1': 'Incoming',
        '2': 'Outgoing',
        '3': 'Missed',
        '4': 'Voicemail',
        '5': 'Rejected',
        '6': 'Blocked'
    }
    type_label = type_map.get(call_type, f'Unknown ({call_type})')
    call_entry = {
        '_id': call_data.get('_id', 'N/A'),
        'number': call_data.get('number', 'N/A'),
        'name': call_data.get('name', 'N/A'),
        'date': formatted_date,
        'date_timestamp': call_data.get('date', 'N/A'),
        'duration': duration_formatted,
        'duration_seconds': duration_str,
        'type': type_label,
        'type_code': call_type,
        'geocoded_location': call_data.get('geocoded_location', 'N/A'),
        'cached_name': call_data.get('cached_name', 'N/A'),
        'cached_number_type': call_data.get('cached_number_type', 'N/A'),
        'cached_number_label': call_data.get('cached_number_label', 'N/A')
    }
    return call_entry


def extract_call_logs_table() -> str:
    call_logs = extract_call_logs()
    if not call_logs:
        return "No call logs found or access denied.\n"
    header = f"{'ID':<8} {'Number':<20} {'Name':<25} {'Type':<12} {'Date':<20} {'Duration':<10}\n"
    separator = "-" * 100 + "\n"
    table = header + separator
    for call in call_logs:
        name = call.get('name', 'N/A')
        if name == 'N/A' and call.get('cached_name') != 'N/A':
            name = call.get('cached_name', 'N/A')
        row = (
            f"{str(call.get('_id', 'N/A')):<8} "
            f"{str(call.get('number', 'N/A')):<20} "
            f"{str(name):<25} "
            f"{str(call.get('type', 'N/A')):<12} "
            f"{str(call.get('date', 'N/A')):<20} "
            f"{str(call.get('duration', 'N/A')):<10}\n"
        )
        table += row
    table += f"\nTotal calls: {len(call_logs)}\n"
    table += f"Incoming: {sum(1 for c in call_logs if c.get('type_code') == '1')}, "
    table += f"Outgoing: {sum(1 for c in call_logs if c.get('type_code') == '2')}, "
    table += f"Missed: {sum(1 for c in call_logs if c.get('type_code') == '3')}\n"
    return table
