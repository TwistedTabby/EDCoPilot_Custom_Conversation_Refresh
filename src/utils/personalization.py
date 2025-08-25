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
        
        # Define valid sections that we want to process
        valid_sections = ['Data', 'Themes', 'RSS Feeds', 'Conversation Styles']
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for headers
            if line.startswith('##'):
                section_name = line.lstrip('##').strip()
                # Only process valid sections
                if section_name in valid_sections:
                    current_section = section_name
                    logger.info(f"📝 Processing section: {current_section}")
                else:
                    current_section = None
                    logger.info(f"⏭️ Skipping section: {section_name}")
                continue
            
            # Check for RSS feeds (only in RSS Feeds section)
            if current_section == 'RSS Feeds' and 'rss' in line.lower() and 'http' in line:
                feed_info = self._extract_rss_feed_info(line)
                if feed_info:
                    self.rss_feeds.append(feed_info)
                    logger.info(f"📡 Found RSS feed: {feed_info['url']} (max entries: {feed_info.get('max_entries', 'all')})")
            
            # Store context data only for valid sections
            if current_section and current_section in valid_sections and line:
                if current_section not in self.context_data:
                    self.context_data[current_section] = []
                
                # Strip any existing "- " prefix to avoid double-formatting
                if line.startswith('- '):
                    line = line[2:]  # Remove the "- " prefix
                
                self.context_data[current_section].append(line)
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    def _extract_rss_feed_info(self, text: str) -> Optional[Dict[str, any]]:
        """Extract RSS feed URL and optional entry limit from text"""
        # Look for pattern like "[2] https://example.com/rss.xml" or just "https://example.com/rss.xml"
        import re
        
        # Pattern to match [number] followed by URL
        pattern = r'\[(\d+)\]\s*(https?://[^\s<>"{}|\\^`\[\]]+)'
        match = re.search(pattern, text)
        
        if match:
            max_entries = int(match.group(1))
            url = match.group(2)
            return {
                'url': url,
                'max_entries': max_entries
            }
        
        # If no bracket pattern, just extract URL (no entry limit)
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        url_match = re.search(url_pattern, text)
        
        if url_match:
            return {
                'url': url_match.group(0),
                'max_entries': None  # No limit specified
            }
        
        return None
    
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
    
    def fetch_rss_content(self, default_max_entries: int = 10) -> Dict[str, List[Dict[str, str]]]:
        """Fetch content from RSS feeds with caching"""
        if not self.rss_feeds:
            logger.info("📡 No RSS feeds configured")
            return {}
        
        rss_content = {}
        
        for feed_info in self.rss_feeds:
            feed_url = feed_info['url']
            max_entries = feed_info.get('max_entries', default_max_entries)
            
            # Try to load from cache first
            cached_data = self._load_cached_rss(feed_url)
            
            if cached_data:
                # Use cached data, but respect the feed's entry limit
                cached_entries = cached_data.get('entries', [])
                if max_entries is not None:
                    cached_entries = cached_entries[:max_entries]
                rss_content[feed_url] = cached_entries
                logger.info(f"📡 Using cached RSS data for {feed_url} ({len(rss_content[feed_url])} entries)")
                continue
            
            # Fetch fresh data if cache is invalid or missing
            try:
                logger.info(f"📡 Fetching fresh RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(f"⚠️ RSS feed parsing warning: {feed.bozo_exception}")
                
                entries = []
                # Use feed-specific max_entries if specified, otherwise use default
                entry_limit = max_entries if max_entries is not None else default_max_entries
                
                for entry in feed.entries[:entry_limit]:
                    title = getattr(entry, 'title', '')
                    summary = getattr(entry, 'summary', '')
                    published = getattr(entry, 'published', '')
                    
                    # Create structured entry data
                    entry_data = {
                        'title': title,
                        'summary': summary,
                        'published': published
                    }
                    
                    entries.append(entry_data)
                
                if entries:
                    rss_content[feed_url] = entries
                    logger.info(f"✅ Fetched {len(entries)} entries from {feed_url}")
                    
                    # Save to cache
                    cache_data = {
                        'entries': entries,
                        'fetched_at': datetime.now(timezone.utc),
                        'max_entries': entry_limit
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
                    # Find the feed info to show entry limit
                    feed_info = next((f for f in self.rss_feeds if f['url'] == feed_url), None)
                    entry_limit = feed_info.get('max_entries', 'all') if feed_info else 'all'
                    context_parts.append(f"### From {feed_url} (max {entry_limit} entries):")
                    
                    for entry in entries:
                        # Title outside code block
                        title = entry.get('title', '')
                        summary = entry.get('summary', '')
                        published = entry.get('published', '')
                        
                        context_parts.append(f"**{title}**")
                        
                        # Content inside code block
                        content_parts = []
                        if summary:
                            content_parts.append(summary)
                        if published:
                            content_parts.append(f"Published: {published}")
                        
                        if content_parts:
                            context_parts.append("```")
                            context_parts.append("\n".join(content_parts))
                            context_parts.append("```")
                        
                        context_parts.append("")
        
        # Add web content if requested
        if include_web:
            # Extract URLs from context data, excluding RSS feed URLs
            all_urls = []
            rss_urls = [feed_info['url'] for feed_info in self.rss_feeds]
            
            for section, items in self.context_data.items():
                for item in items:
                    urls = self._extract_urls(item)
                    # Filter out RSS feed URLs to avoid duplicate fetching
                    for url in urls:
                        if url not in rss_urls:
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
    
    def get_data_section(self) -> str:
        """Get formatted data section for template variables"""
        if 'Data' in self.context_data:
            items = self.context_data['Data']
            return '\n'.join([f"- {item}" for item in items])
        return ""
    
    def get_themes_section(self) -> str:
        """Get formatted themes section for template variables"""
        if 'Themes' in self.context_data:
            items = self.context_data['Themes']
            # Always add "- " prefix since we strip it during parsing
            return '\n'.join([f"- {item}" for item in items])
        return ""
    
    def get_conversation_styles_section(self) -> str:
        """Get formatted conversation styles section for template variables"""
        if 'Conversation Styles' in self.context_data:
            items = self.context_data['Conversation Styles']
            # Always add "- " prefix since we strip it during parsing
            return '\n'.join([f"- {item}" for item in items])
        return ""
    
    def get_rss_summary(self) -> str:
        """Get formatted RSS summary for template variables"""
        if not self.rss_feeds:
            return ""
        
        rss_content = self.fetch_rss_content()
        if not rss_content:
            return ""
        
        summary_parts = []
        for feed_url, entries in rss_content.items():
            feed_info = next((f for f in self.rss_feeds if f['url'] == feed_url), None)
            entry_limit = feed_info.get('max_entries', 'all') if feed_info else 'all'
            summary_parts.append(f"### From {feed_url} (max {entry_limit} entries):")
            
            for entry in entries:
                # Title outside code block
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                published = entry.get('published', '')
                
                summary_parts.append(f"**{title}**")
                
                # Content inside code block
                content_parts = []
                if summary:
                    content_parts.append(summary)
                if published:
                    content_parts.append(f"Published: {published}")
                
                if content_parts:
                    summary_parts.append("```")
                    summary_parts.append("\n".join(content_parts))
                    summary_parts.append("```")
                
                summary_parts.append("")
        
        return '\n'.join(summary_parts)
    
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
