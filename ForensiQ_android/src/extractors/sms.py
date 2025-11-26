from typing import List, Dict
from ..utils import run_adb_command, parse_date
import re


def extract_sms() -> List[Dict]:
    sms_messages = []
    output = run_adb_command('shell content query --uri content://sms --projection _id,address,body,read,date,type')
    if not output:
        return sms_messages
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
                    sms_data = parse_content_query_row(current_row_data)
                    if sms_data:
                        sms_messages.append(create_sms_entry(sms_data))
                except:
                    pass
            current_row = line
            current_row_data = [line]
        elif current_row is not None:
            current_row_data.append(line)
    if current_row is not None:
        try:
            sms_data = parse_content_query_row(current_row_data)
            if sms_data:
                sms_messages.append(create_sms_entry(sms_data))
        except:
            pass
    return sms_messages


def parse_content_query_row(row_lines):
    full_text = ' '.join(row_lines)
    data_part = re.sub(r'^Row: \d+ ', '', full_text)
    parts = re.split(r',\s*(?=\w+=)', data_part)
    sms_data = {}
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
                sms_data[key] = value
    return sms_data


def create_sms_entry(sms_data):
    date_str = sms_data.get('date', '0')
    formatted_date = parse_date(date_str) if date_str and date_str.isdigit() else 'N/A'
    sms_type = str(sms_data.get('type', '0'))
    type_map = {
        '1': 'Inbox',
        '2': 'Sent',
        '3': 'Draft',
        '4': 'Outbox',
        '5': 'Failed',
        '6': 'Queued'
    }
    type_label = type_map.get(sms_type, f'Unknown ({sms_type})')
    read_status = 'Read' if str(sms_data.get('read', '0')) == '1' else 'Unread'
    sms_entry = {
        '_id': sms_data.get('_id', 'N/A'),
        'address': sms_data.get('address', 'N/A'),
        'body': sms_data.get('body', 'N/A'),
        'read': read_status,
        'date': formatted_date,
        'date_timestamp': sms_data.get('date', 'N/A'),
        'type': type_label,
        'type_code': sms_type
    }
    return sms_entry


def extract_sms_table() -> str:
    sms_messages = extract_sms()
    if not sms_messages:
        return "No SMS messages found or access denied.\n"
    header = f"{'ID':<8} {'Address':<20} {'Type':<10} {'Read':<8} {'Date':<20} {'Message':<50}\n"
    separator = "-" * 120 + "\n"
    table = header + separator
    for sms in sms_messages:
        body = str(sms.get('body', 'N/A'))
        if len(body) > 47:
            body = body[:44] + "..."
        row = (
            f"{str(sms.get('_id', 'N/A')):<8} "
            f"{str(sms.get('address', 'N/A')):<20} "
            f"{str(sms.get('type', 'N/A')):<10} "
            f"{str(sms.get('read', 'N/A')):<8} "
            f"{str(sms.get('date', 'N/A')):<20} "
            f"{body:<50}\n"
        )
        table += row
    table += f"\nTotal SMS messages: {len(sms_messages)}\n"
    table += f"Inbox: {sum(1 for s in sms_messages if s.get('type_code') == '1')}, "
    table += f"Sent: {sum(1 for s in sms_messages if s.get('type_code') == '2')}\n"
    return table
