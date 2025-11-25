"""
Export utilities for ForensiQ reports
Supports PDF, CSV, JSON, and ZIP exports
"""
import os
import json
import csv
import zipfile
from datetime import datetime
from typing import List, Dict, Any

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: reportlab not installed. PDF export disabled. Install with: pip install reportlab")

def export_to_csv(data: List[Dict[str, Any]], filename: str, headers: List[str] = None):
    """Export data to CSV file."""
    if not data:
        return False
    
    try:
        if headers is None:
            headers = list(data[0].keys()) if data else []
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

def export_to_json(data: Any, filename: str):
    """Export data to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=4, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False

def export_to_pdf(html_content: str, filename: str, title: str = "ForensiQ Report"):
    """Export HTML report to PDF."""
    if not PDF_AVAILABLE:
        return False
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Extract tables
        tables = soup.find_all('table')
        for table in tables:
            # Extract headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text().strip() for th in header_row.find_all('th')]
            
            # Extract data
            data = []
            tbody = table.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    cells = [td.get_text().strip() for td in row.find_all('td')]
                    if cells:
                        data.append(cells)
            
            if headers and data:
                # Create table data with headers
                table_data = [headers] + data
                
                # Create PDF table
                pdf_table = Table(table_data)
                pdf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                ]))
                
                story.append(pdf_table)
                story.append(Spacer(1, 0.3*inch))
        
        doc.build(story)
        return True
    except ImportError:
        print("Warning: BeautifulSoup4 not installed. Install with: pip install beautifulsoup4")
        return False
    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        return False

def export_all_reports_to_zip(output_dir: str, zip_filename: str = None):
    """Export all reports to a ZIP file."""
    if zip_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"ForensiQ_Reports_{timestamp}.zip"
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all HTML files
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.html') or file.endswith('.json') or file.endswith('.csv'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)
        
        return zip_filename
    except Exception as e:
        print(f"Error creating ZIP: {e}")
        return None

def parse_html_table(html_content: str) -> tuple:
    """Parse HTML table and return headers and data."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return [], []
        
        headers = []
        thead = table.find('thead')
        if thead:
            headers = [th.get_text().strip() for th in thead.find_all('th')]
        
        data = []
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cells = [td.get_text().strip() for td in row.find_all('td')]
                if cells:
                    data.append(dict(zip(headers, cells)) if headers else cells)
        
        return headers, data
    except ImportError:
        print("Warning: BeautifulSoup4 not installed")
        return [], []
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return [], []

