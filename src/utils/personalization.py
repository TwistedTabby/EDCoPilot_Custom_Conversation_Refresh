"""
Personalization module for EDCopilot Chit Chat Updater
Handles user-specific context and web searching capabilities
"""

import os
import re
import json
import pickle
import logging
import requests
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse
import feedparser
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class PersonalizationManager:
    """Manages personalization context and web searching"""
    
    def __init__(self, personalization_file: str = "personalization.md", cache_dir: str = "cache"):
        self.personalization_file = Path(personalization_file)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.context_data = {}
        self.rss_feeds = []
        self.web_content = {}
        self.rss_cache = {}
        self.cache_duration = timedelta(hours=8)  # Cache for 8 hours
        self._load_personalization()
    
    def _load_personalization(self):
        """Load personalization data from the markdown file"""
        if not self.personalization_file.exists():
            logger.warning(f"⚠️ Personalization file not found: {self.personalization_file}")
            return
        
        try:
            with open(self.personalization_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._parse_personalization_content(content)
            logger.info(f"✅ Loaded personalization data: {len(self.context_data)} items")
            
        except Exception as e:
            logger.error(f"❌ Failed to load personalization file: {str(e)}")
    
    def _parse_personalization_content(self, content: str):
        """Parse the personalization markdown content"""
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for headers
            if line.startswith('#'):
                current_section = line.lstrip('#').strip()
                continue
            
            # Check for RSS feeds
            if 'rss' in line.lower() and 'http' in line:
                urls = self._extract_urls(line)
                self.rss_feeds.extend(urls)
                logger.info(f"📡 Found RSS feeds: {urls}")
            
            # Store context data
            if current_section and line:
                if current_section not in self.context_data:
                    self.context_data[current_section] = []
                self.context_data[current_section].append(line)
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    def _get_cache_file_path(self, feed_url: str) -> Path:
        """Get the cache file path for a feed URL"""
        # Create a safe filename from the URL
        safe_filename = re.sub(r'[^\w\-_.]', '_', feed_url)
        return self.cache_dir / f"rss_cache_{safe_filename}.pkl"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if the cache file is still valid (within 8 hours)"""
        if not cache_file.exists():
            return False
        
        try:
            # Check file modification time
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            age = now - mtime
            
            return age < self.cache_duration
        except Exception as e:
            logger.warning(f"⚠️ Error checking cache validity: {str(e)}")
            return False
    
    def _load_cached_rss(self, feed_url: str) -> Optional[Dict]:
        """Load RSS content from cache if valid"""
        cache_file = self._get_cache_file_path(feed_url)
        
        if not self._is_cache_valid(cache_file):
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                logger.info(f"📡 Loaded RSS cache for {feed_url}")
                return cached_data
        except Exception as e:
            logger.warning(f"⚠️ Failed to load RSS cache for {feed_url}: {str(e)}")
            return None
    
    def _save_rss_cache(self, feed_url: str, rss_data: Dict):
        """Save RSS content to cache"""
        cache_file = self._get_cache_file_path(feed_url)
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(rss_data, f)
                logger.info(f"📡 Saved RSS cache for {feed_url}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save RSS cache for {feed_url}: {str(e)}")
    
    def fetch_rss_content(self, max_entries: int = 10) -> Dict[str, List[str]]:
        """Fetch content from RSS feeds with caching"""
        if not self.rss_feeds:
            logger.info("📡 No RSS feeds configured")
            return {}
        
        rss_content = {}
        
        for feed_url in self.rss_feeds:
            # Try to load from cache first
            cached_data = self._load_cached_rss(feed_url)
            
            if cached_data:
                # Use cached data
                rss_content[feed_url] = cached_data.get('entries', [])
                logger.info(f"📡 Using cached RSS data for {feed_url} ({len(rss_content[feed_url])} entries)")
                continue
            
            # Fetch fresh data if cache is invalid or missing
            try:
                logger.info(f"📡 Fetching fresh RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(f"⚠️ RSS feed parsing warning: {feed.bozo_exception}")
                
                entries = []
                for entry in feed.entries[:max_entries]:
                    title = getattr(entry, 'title', '')
                    summary = getattr(entry, 'summary', '')
                    published = getattr(entry, 'published', '')
                    
                    entry_text = f"Title: {title}"
                    if summary:
                        entry_text += f" | Summary: {summary}"
                    if published:
                        entry_text += f" | Published: {published}"
                    
                    entries.append(entry_text)
                
                if entries:
                    rss_content[feed_url] = entries
                    logger.info(f"✅ Fetched {len(entries)} entries from {feed_url}")
                    
                    # Save to cache
                    cache_data = {
                        'entries': entries,
                        'fetched_at': datetime.now(timezone.utc),
                        'max_entries': max_entries
                    }
                    self._save_rss_cache(feed_url, cache_data)
                
            except Exception as e:
                logger.error(f"❌ Failed to fetch RSS feed {feed_url}: {str(e)}")
        
        return rss_content
    
    def fetch_web_content(self, urls: List[str], max_content_length: int = 1000) -> Dict[str, str]:
        """Fetch content from web URLs"""
        web_content = {}
        
        for url in urls:
            try:
                logger.info(f"🌐 Fetching web content: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Extract text content (basic implementation)
                content = self._extract_text_content(response.text)
                
                if content:
                    # Truncate if too long
                    if len(content) > max_content_length:
                        content = content[:max_content_length] + "..."
                    
                    web_content[url] = content
                    logger.info(f"✅ Fetched {len(content)} characters from {url}")
                
            except Exception as e:
                logger.error(f"❌ Failed to fetch web content {url}: {str(e)}")
        
        return web_content
    
    def _extract_text_content(self, html_content: str) -> str:
        """Extract text content from HTML (basic implementation)"""
        # Remove HTML tags
        import re
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        return text.strip()
    
    def get_personalization_context(self, include_rss: bool = True, include_web: bool = True) -> str:
        """Get formatted personalization context for API calls"""
        context_parts = []
        
        # Add basic context data
        if self.context_data:
            context_parts.append("## Personal Context:")
            for section, items in self.context_data.items():
                context_parts.append(f"### {section}:")
                for item in items:
                    context_parts.append(f"- {item}")
                context_parts.append("")
        
        # Add RSS content if requested
        if include_rss and self.rss_feeds:
            rss_content = self.fetch_rss_content()
            if rss_content:
                context_parts.append("## Recent News and Updates:")
                for feed_url, entries in rss_content.items():
                    context_parts.append(f"### From {feed_url}:")
                    for entry in entries:
                        context_parts.append(f"- {entry}")
                    context_parts.append("")
        
        # Add web content if requested
        if include_web:
            # Extract URLs from context data, excluding RSS feed URLs
            all_urls = []
            for section, items in self.context_data.items():
                for item in items:
                    urls = self._extract_urls(item)
                    # Filter out RSS feed URLs to avoid duplicate fetching
                    for url in urls:
                        if url not in self.rss_feeds:
                            all_urls.append(url)
            
            if all_urls:
                web_content = self.fetch_web_content(all_urls)
                if web_content:
                    context_parts.append("## Web Content References:")
                    for url, content in web_content.items():
                        context_parts.append(f"### {url}:")
                        context_parts.append(content)
                        context_parts.append("")
        
        return "\n".join(context_parts)
    
    def get_user_preferences(self) -> Dict[str, any]:
        """Extract user preferences from context data"""
        preferences = {}
        
        # Extract specific data points
        for section, items in self.context_data.items():
            section_lower = section.lower()
            
            if 'commander' in section_lower or 'name' in section_lower:
                for item in items:
                    if ':' in item:
                        key, value = item.split(':', 1)
                        preferences[key.strip()] = value.strip()
            
            elif 'squadron' in section_lower:
                for item in items:
                    if ':' in item:
                        key, value = item.split(':', 1)
                        preferences[key.strip()] = value.strip()
            
            elif 'theme' in section_lower:
                themes = []
                for item in items:
                    if item.startswith('-'):
                        themes.append(item[1:].strip())
                    else:
                        themes.append(item)
                preferences['themes'] = themes
            
            elif 'fleet' in section_lower and 'carrier' in section_lower:
                for item in items:
                    if ':' in item:
                        key, value = item.split(':', 1)
                        preferences[key.strip()] = value.strip()
        
        return preferences
    
    def get_content_guidelines(self) -> List[str]:
        """Extract content guidelines and preferences"""
        guidelines = []
        
        for section, items in self.context_data.items():
            section_lower = section.lower()
            
            if 'notes' in section_lower or 'guidelines' in section_lower or 'preferences' in section_lower:
                for item in items:
                    if item.startswith('-'):
                        guidelines.append(item[1:].strip())
                    else:
                        guidelines.append(item)
        
        return guidelines
    
    def clear_rss_cache(self, feed_url: Optional[str] = None):
        """Clear RSS cache for a specific feed or all feeds"""
        if feed_url:
            # Clear cache for specific feed
            cache_file = self._get_cache_file_path(feed_url)
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"🗑️ Cleared RSS cache for {feed_url}")
        else:
            # Clear all RSS cache files
            cache_files = list(self.cache_dir.glob("rss_cache_*.pkl"))
            for cache_file in cache_files:
                cache_file.unlink()
            logger.info(f"🗑️ Cleared all RSS cache files ({len(cache_files)} files)")
    
    def get_cache_info(self) -> Dict[str, any]:
        """Get information about the RSS cache"""
        cache_info = {
            'cache_dir': str(self.cache_dir),
            'cache_duration_hours': self.cache_duration.total_seconds() / 3600,
            'cached_feeds': []
        }
        
        cache_files = list(self.cache_dir.glob("rss_cache_*.pkl"))
        for cache_file in cache_files:
            if self._is_cache_valid(cache_file):
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime, tz=timezone.utc)
                age = datetime.now(timezone.utc) - mtime
                cache_info['cached_feeds'].append({
                    'file': cache_file.name,
                    'age_hours': age.total_seconds() / 3600,
                    'valid': True
                })
            else:
                cache_info['cached_feeds'].append({
                    'file': cache_file.name,
                    'age_hours': None,
                    'valid': False
                })
        
        return cache_info
