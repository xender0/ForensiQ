"""
Report archiving system for ForensiQ
Manages historical reports with timestamps
"""
import os
import shutil
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from config_manager import ConfigManager

class ReportArchiver:
    def __init__(self, config_manager: ConfigManager, output_dir: str = "output"):
        self.config = config_manager
        self.output_dir = output_dir
        self.archive_dir = os.path.join(output_dir, "archive")
        self.ensure_archive_dir()
    
    def ensure_archive_dir(self):
        """Ensure archive directory exists."""
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
    
    def archive_current_reports(self) -> str:
        """Archive all current reports with timestamp."""
        if not self.config.get_setting("archive_reports", True):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"scan_{timestamp}"
        archive_path = os.path.join(self.archive_dir, archive_name)
        
        try:
            os.makedirs(archive_path, exist_ok=True)
            
            # Copy all HTML reports
            for file in os.listdir(self.output_dir):
                if file.endswith('.html') and file != 'index.html':
                    src = os.path.join(self.output_dir, file)
                    dst = os.path.join(archive_path, file)
                    shutil.copy2(src, dst)
            
            # Copy manifest
            manifest_src = os.path.join(self.output_dir, "manifest.json")
            if os.path.exists(manifest_src):
                shutil.copy2(manifest_src, os.path.join(archive_path, "manifest.json"))
            
            # Save archive metadata
            metadata = {
                "timestamp": timestamp,
                "created": datetime.now().isoformat(),
                "reports": [f for f in os.listdir(archive_path) if f.endswith('.html')]
            }
            
            with open(os.path.join(archive_path, "metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=4)
            
            return archive_path
        except Exception as e:
            print(f"Error archiving reports: {e}")
            return None
    
    def get_archives(self) -> List[Dict[str, Any]]:
        """Get list of all archives."""
        archives = []
        
        if not os.path.exists(self.archive_dir):
            return archives
        
        for item in os.listdir(self.archive_dir):
            archive_path = os.path.join(self.archive_dir, item)
            if os.path.isdir(archive_path):
                metadata_path = os.path.join(archive_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            metadata['path'] = archive_path
                            metadata['name'] = item
                            archives.append(metadata)
                    except:
                        pass
        
        # Sort by timestamp (newest first)
        archives.sort(key=lambda x: x.get('created', ''), reverse=True)
        return archives
    
    def cleanup_old_archives(self):
        """Remove archives older than retention period."""
        retention_days = self.config.get_setting("archive_retention_days", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        archives = self.get_archives()
        deleted = 0
        
        for archive in archives:
            try:
                created = datetime.fromisoformat(archive.get('created', ''))
                if created < cutoff_date:
                    archive_path = archive.get('path')
                    if archive_path and os.path.exists(archive_path):
                        shutil.rmtree(archive_path)
                        deleted += 1
            except:
                pass
        
        return deleted
    
    def restore_archive(self, archive_name: str) -> bool:
        """Restore an archive to current reports."""
        archive_path = os.path.join(self.archive_dir, archive_name)
        
        if not os.path.exists(archive_path):
            return False
        
        try:
            # Backup current reports first
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join(self.archive_dir, backup_name)
            if os.path.exists(self.output_dir):
                shutil.copytree(self.output_dir, backup_path, dirs_exist_ok=True)
            
            # Copy archived reports
            for file in os.listdir(archive_path):
                if file.endswith('.html') or file == 'manifest.json':
                    src = os.path.join(archive_path, file)
                    dst = os.path.join(self.output_dir, file)
                    shutil.copy2(src, dst)
            
            return True
        except Exception as e:
            print(f"Error restoring archive: {e}")
            return False

