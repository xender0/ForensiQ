from typing import List, Dict
from ..utils import run_adb_command, parse_date
import re


def extract_contacts() -> List[Dict]:
    contacts = []
    output = run_adb_command('shell content query --uri content://com.android.contacts/data/phones')
    if not output:
        return contacts
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
                    contact_data = parse_content_query_row(current_row_data)
                    if contact_data:
                        contacts.append(create_contact_entry(contact_data))
                except:
                    pass
            current_row = line
            current_row_data = [line]
        elif current_row is not None:
            current_row_data.append(line)
    if current_row is not None:
        try:
            contact_data = parse_content_query_row(current_row_data)
            if contact_data:
                contacts.append(create_contact_entry(contact_data))
        except:
            pass
    return contacts


def parse_content_query_row(row_lines):
    full_text = ' '.join(row_lines)
    data_part = re.sub(r'^Row: \d+ ', '', full_text)
    parts = re.split(r',\s*(?=\w+=)', data_part)
    contact_data = {}
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
                contact_data[key] = value
    return contact_data


def create_contact_entry(contact_data):
    contact_entry = {
        '_id': contact_data.get('_id', 'N/A'),
        'display_name': contact_data.get('display_name', 'N/A'),
        'phone_number': contact_data.get('data1', 'N/A'),
        'phone_type': contact_data.get('data2', 'N/A'),
        'raw_contact_id': contact_data.get('raw_contact_id', 'N/A'),
        'contact_id': contact_data.get('contact_id', 'N/A'),
        'mimetype': contact_data.get('mimetype', 'N/A')
    }
    return contact_entry


def extract_contacts_table() -> str:
    contacts = extract_contacts()
    if not contacts:
        return "No contacts found or access denied.\n"
    header = f"{'ID':<8} {'Name':<30} {'Phone Number':<20} {'Type':<15} {'Contact ID':<12}\n"
    separator = "-" * 100 + "\n"
    table = header + separator
    for contact in contacts:
        row = (
            f"{str(contact.get('_id', 'N/A')):<8} "
            f"{str(contact.get('display_name', 'N/A')):<30} "
            f"{str(contact.get('phone_number', 'N/A')):<20} "
            f"{str(contact.get('phone_type', 'N/A')):<15} "
            f"{str(contact.get('contact_id', 'N/A')):<12}\n"
        )
        table += row
    table += f"\nTotal contacts: {len(contacts)}\n"
    return table
