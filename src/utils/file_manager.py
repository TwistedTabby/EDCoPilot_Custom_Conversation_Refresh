"""
File Manager module for EDCopilot Chit Chat Updater
Handles file operations, backups, and content management
"""

import os
import shutil
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict
from pathlib import Path
from src.config import Config

logger = logging.getLogger(__name__)

class FileManager:
    """File Manager for handling EDCopilot custom chatter files"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.custom_dir = Path(Config.CUSTOM_DIR)
        self.backup_dir = Path("backups")
        self.output_dir = Path("output")
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        self.backup_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Ensure custom directory exists if not in debug mode
        if not self.debug_mode:
            self.custom_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Custom directory ensured: {self.custom_dir}")
        
        logger.info(f"📁 Directories ensured: {self.backup_dir}, {self.output_dir}")
    
    def get_output_path(self, filename: str) -> Path:
        """
        Get the correct output path based on debug mode
        
        Args:
            filename: Name of the file (e.g., 'EDCoPilot.ChitChat.Custom.txt')
            
        Returns:
            Path to the output file
        """
        if self.debug_mode:
            # In debug mode, write to project output directory
            return self.output_dir / filename
        else:
            # In production mode, write to EDCopilot custom directory
            return self.custom_dir / filename
    
    def get_chatter_files(self) -> Dict[str, Path]:
        """Get the paths to all chatter files"""
        files = {
            'ChitChat': self.custom_dir / 'EDCoPilot.ChitChat.Custom.txt',
            'SpaceChatter': self.custom_dir / 'EDCoPilot.SpaceChatter.Custom.txt',
            'CrewChatter': self.custom_dir / 'EDCoPilot.CrewChatter.Custom.txt',
            'DeepSpaceChatter': self.custom_dir / 'EDCoPilot.DeepSpaceChatter.Custom.txt'
        }
        
        # Check which files exist
        existing_files = {}
        for name, path in files.items():
            if path.exists():
                existing_files[name] = path
                logger.info(f"📄 Found existing file: {name} -> {path}")
            else:
                logger.warning(f"⚠️ File not found: {name} -> {path}")
        
        return existing_files
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create a backup of the specified file
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file or None if backup failed
        """
        if not file_path.exists():
            logger.warning(f"⚠️ Cannot backup non-existent file: {file_path}")
            return None
        
        try:
            # Create timestamp for backup filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self.backup_dir / backup_filename
            
            # Copy the file
            shutil.copy2(file_path, backup_path)
            logger.info(f"💾 Backup created: {file_path} -> {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Backup failed for {file_path}: {str(e)}")
            return None
    
    def create_backup_all(self) -> Dict[str, Optional[Path]]:
        """Create backups of all existing chatter files"""
        existing_files = self.get_chatter_files()
        backups = {}
        
        for name, file_path in existing_files.items():
            backup_path = self.create_backup(file_path)
            backups[name] = backup_path
        
        return backups
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """Read content from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"📖 Read {len(content)} characters from {file_path}")
            return content
        except Exception as e:
            logger.error(f"❌ Failed to read {file_path}: {str(e)}")
            return None
    
    def write_file_content(self, file_path: Path, content: str) -> bool:
        """Write content to a file"""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"📝 Wrote {len(content)} characters to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to write {file_path}: {str(e)}")
            return False
    
    def write_content(self, file_path: str, content: str) -> bool:
        """
        Write content to a file using a string path
        
        Args:
            file_path: String path to the file
            content: Content to write
            
        Returns:
            True if successful
        """
        path = Path(file_path)
        return self.write_file_content(path, content)
    
    def merge_content(self, file_path: str, new_content: str, max_lines: int = 100) -> bool:
        """
        Merge new content with existing content in a file
        
        Args:
            file_path: String path to the file
            new_content: New content to add
            max_lines: Maximum number of lines to keep in total
            
        Returns:
            True if successful
        """
        path = Path(file_path)
        
        # Create backup if file exists
        if path.exists():
            backup_path = self.create_backup(path)
            if not backup_path:
                logger.error(f"❌ Failed to create backup for {file_path}")
                return False
        
        # Read existing content
        existing_content = self.read_file_content(path) if path.exists() else ""
        
        # Merge content
        merged_content = self._merge_content_strings(existing_content, new_content, max_lines)
        
        # Write merged content
        return self.write_file_content(path, merged_content)
    
    def _merge_content_strings(self, existing_content: str, new_content: str, max_lines: int = 100) -> str:
        """
        Merge new content with existing content, avoiding duplicates
        
        Args:
            existing_content: Current file content
            new_content: New content to add
            max_lines: Maximum number of lines to keep in total
            
        Returns:
            Merged content string
        """
        # Split content into lines
        existing_lines = [line.strip() for line in existing_content.split('\n') if line.strip()]
        new_lines = [line.strip() for line in new_content.split('\n') if line.strip()]
        
        # Remove duplicates (case-insensitive)
        existing_lower = set(line.lower() for line in existing_lines)
        unique_new_lines = [line for line in new_lines if line.lower() not in existing_lower]
        
        # Combine and limit total lines
        combined_lines = existing_lines + unique_new_lines
        if len(combined_lines) > max_lines:
            combined_lines = combined_lines[-max_lines:]  # Keep most recent
        
        # Join back into content
        merged_content = '\n'.join(combined_lines)
        
        logger.info(f"🔄 Merged content: {len(existing_lines)} existing + {len(unique_new_lines)} new = {len(combined_lines)} total")
        return merged_content
    
    def validate_content(self, content: str) -> bool:
        """
        Validate content for basic quality checks
        
        Args:
            content: Content to validate
            
        Returns:
            True if content passes validation
        """
        if not content or not content.strip():
            logger.warning("⚠️ Content is empty")
            return False
        
        # Check for minimum content length
        if len(content.strip()) < 50:
            logger.warning("⚠️ Content too short")
            return False
        
        # Check for inappropriate content (basic filter)
        inappropriate_words = ['inappropriate', 'offensive', 'spam']
        content_lower = content.lower()
        for word in inappropriate_words:
            if word in content_lower:
                logger.warning(f"⚠️ Content contains inappropriate word: {word}")
                return False
        
        logger.info("✅ Content validation passed")
        return True
    
    def deploy_content(self, chatter_type: str, content: str) -> bool:
        """
        Deploy content to the appropriate EDCopilot file
        
        Args:
            chatter_type: Type of chatter (ChitChat, SpaceChatter, etc.)
            content: Content to deploy
            
        Returns:
            True if deployment successful
        """
        # Create backup first
        file_path = self.custom_dir / f'EDCoPilot.{chatter_type}.Custom.txt'
        if file_path.exists():
            backup_path = self.create_backup(file_path)
            if not backup_path:
                logger.error(f"❌ Failed to create backup for {chatter_type}")
                return False
        
        # Validate content
        if not self.validate_content(content):
            logger.error(f"❌ Content validation failed for {chatter_type}")
            return False
        
        # Write content
        if self.write_file_content(file_path, content):
            logger.info(f"✅ Successfully deployed {chatter_type} content")
            return True
        else:
            logger.error(f"❌ Failed to deploy {chatter_type} content")
            return False
    
    def rollback_file(self, chatter_type: str) -> bool:
        """
        Rollback a file to its most recent backup
        
        Args:
            chatter_type: Type of chatter to rollback
            
        Returns:
            True if rollback successful
        """
        file_path = self.custom_dir / f'EDCoPilot.{chatter_type}.Custom.txt'
        
        # Find most recent backup
        backup_pattern = f"EDCoPilot.{chatter_type}_*"
        backup_files = list(self.backup_dir.glob(backup_pattern))
        
        if not backup_files:
            logger.warning(f"⚠️ No backups found for {chatter_type}")
            return False
        
        # Get most recent backup
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        
        try:
            # Restore from backup
            shutil.copy2(latest_backup, file_path)
            logger.info(f"🔄 Rolled back {chatter_type} to {latest_backup}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed for {chatter_type}: {str(e)}")
            return False
    
    def get_file_info(self) -> Dict[str, Dict]:
        """Get information about all chatter files"""
        files = self.get_chatter_files()
        info = {}
        
        for name, file_path in files.items():
            try:
                stat = file_path.stat()
                content = self.read_file_content(file_path)
                
                info[name] = {
                    'path': str(file_path),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                    'lines': len(content.split('\n')) if content else 0,
                    'exists': True
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to get info for {name}: {str(e)}")
                info[name] = {'exists': False, 'error': str(e)}
        
        return info
