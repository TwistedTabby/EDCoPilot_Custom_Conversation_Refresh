"""
Main orchestrator for EDCopilot Chit Chat Updater
Coordinates content generation and deployment for all chatter types
"""

# Suppress the platform independent libraries warning
import os
import sys

# Suppress the warning by setting environment variables
os.environ['PYTHONPATH'] = ''
os.environ['PYTHONHOME'] = ''

# Also try to suppress the warning by redirecting stderr temporarily
class SuppressWarning:
    def __enter__(self):
        self.original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self.original_stderr

# Use the context manager to suppress the warning
with SuppressWarning():
    pass

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from colorama import Fore, Style, init
from tqdm import tqdm

from src.config import Config
from src.generators.chit_chat_generator import ChitChatGenerator
from src.generators.crew_chatter_generator import CrewChatterGenerator
from src.generators.deep_space_chatter_generator import DeepSpaceChatterGenerator
from src.generators.space_chatter_generator import SpaceChatterGenerator

# Initialize colorama for cross-platform colored output
init()

class EDCopilotUpdater:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.generators = {
            'chit_chat': ChitChatGenerator(debug_mode=debug_mode),
            'space_chatter': SpaceChatterGenerator(debug_mode=debug_mode),
            'crew_chatter': CrewChatterGenerator(debug_mode=debug_mode),
            'deep_space_chatter': DeepSpaceChatterGenerator(debug_mode=debug_mode)
        }
        self._setup_logging(debug_mode)

    def _setup_logging(self, debug_mode: bool = False):
        """Setup logging configuration"""
        if debug_mode:
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f'edcopilot_updater_{timestamp}.log'
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        else:
            # Only console output when not in debug mode
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(sys.stdout)
                ]
            )

    def validate_setup(self) -> bool:
        """Validate the current setup"""
        print(f"{Fore.BLUE}🔍 Validating setup...{Style.RESET_ALL}")
        
        # Check environment variables
        if not Config.validate():
            print(f"{Fore.RED}❌ Environment validation failed{Style.RESET_ALL}")
            return False
        
        # Check output directory
        output_dir = Path('output')
        if not output_dir.exists():
            output_dir.mkdir(exist_ok=True)
            print(f"{Fore.YELLOW}📁 Created output directory{Style.RESET_ALL}")
        
        # Check generators
        for name, generator in self.generators.items():
            if not generator.validate_setup():
                print(f"{Fore.RED}❌ {name} generator validation failed{Style.RESET_ALL}")
                return False
        
        print(f"{Fore.GREEN}✅ Setup validation passed{Style.RESET_ALL}")
        return True

    def run(self, merge_existing: bool = False, include_personalization: bool = True,
            include_rss: bool = True, include_web: bool = True, debug_mode: bool = False,
            specific_files: Optional[list] = None, max_entries: int = 5, prompt_only: bool = False) -> bool:
        """Run the EDCopilot updater"""
        if prompt_only:
            print(f"{Fore.BLUE}🚀 Starting EDCopilot Prompt Generator{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}🚀 Starting EDCopilot Conversation Refresher{Style.RESET_ALL}")
        
        if not self.validate_setup():
            return False
        
        if prompt_only:
            if specific_files:
                results = self.generate_prompts_only(specific_files, max_entries, 
                                                   include_personalization, include_rss, include_web)
            else:
                results = self.generate_all_prompts(include_personalization, include_rss, include_web, max_entries)
        else:
            if specific_files:
                results = self.generate_specific_content(specific_files, max_entries, 
                                                       merge_existing, include_personalization,
                                                       include_rss, include_web, debug_mode)
            else:
                results = self.generate_all_content(merge_existing, include_personalization,
                                                  include_rss, include_web, debug_mode, max_entries)
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\n{Fore.BLUE}📊 Results Summary:{Style.RESET_ALL}")
        for chatter_type, success in results.items():
            status = f"{Fore.GREEN}✅{Style.RESET_ALL}" if success else f"{Fore.RED}❌{Style.RESET_ALL}"
            print(f"  {status} {chatter_type}")
        
        if prompt_only:
            print(f"\n{Fore.GREEN}🎉 Completed! {success_count}/{total_count} prompts generated{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}🎉 Completed! {success_count}/{total_count} generators succeeded{Style.RESET_ALL}")
        return success_count == total_count

    def generate_specific_content(self, file_types: list, max_entries: int, 
                                merge_existing: bool = False, include_personalization: bool = True,
                                include_rss: bool = True, include_web: bool = True, 
                                debug_mode: bool = False) -> Dict[str, bool]:
        """Generate content for specific file types"""
        print(f"{Fore.BLUE}🎯 Generating content for specific files: {', '.join(file_types)}...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 Max entries per file: {max_entries}{Style.RESET_ALL}")
        
        # Show personalization status
        if include_personalization:
            print(f"{Fore.CYAN}🎯 Personalization: Enabled{Style.RESET_ALL}")
            if include_rss:
                print(f"{Fore.CYAN}📡 RSS Feeds: Enabled{Style.RESET_ALL}")
            if include_web:
                print(f"{Fore.CYAN}🌐 Web Content: Enabled{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ Personalization: Disabled{Style.RESET_ALL}")
        
        if debug_mode:
            print(f"{Fore.MAGENTA}🐛 Debug Mode: Enabled - Content will be displayed in shell{Style.RESET_ALL}")

        results = {}
        with tqdm(total=len(file_types), desc="Generating content",
                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            for file_type in file_types:
                if file_type not in self.generators:
                    print(f"{Fore.RED}❌ Unknown file type: {file_type}{Style.RESET_ALL}")
                    results[file_type] = False
                    pbar.update(1)
                    continue
                
                try:
                    pbar.set_description(f"Generating {file_type}")
                    generator = self.generators[file_type]
                    
                    success = generator.process_and_deploy(
                        merge_existing=merge_existing,
                        include_personalization=include_personalization,
                        include_rss=include_rss,
                        include_web=include_web,
                        debug_mode=debug_mode,
                        max_entries=max_entries
                    )
                    results[file_type] = success
                    
                    if success:
                        pbar.set_postfix_str(f"{Fore.GREEN}✅{Style.RESET_ALL}")
                    else:
                        pbar.set_postfix_str(f"{Fore.RED}❌{Style.RESET_ALL}")
                        
                except Exception as e:
                    print(f"\n{Fore.RED}❌ Error generating {file_type}: {str(e)}{Style.RESET_ALL}")
                    results[file_type] = False
                    pbar.set_postfix_str(f"{Fore.RED}❌{Style.RESET_ALL}")
                
                pbar.update(1)
        
        return results

    def generate_all_content(self, merge_existing: bool = False, include_personalization: bool = True,
                           include_rss: bool = True, include_web: bool = True, 
                           debug_mode: bool = False, max_entries: int = 5) -> Dict[str, bool]:
        """Generate content for all chatter types"""
        print(f"{Fore.BLUE}🚀 Generating content for all chatter types...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 Max entries per file: {max_entries}{Style.RESET_ALL}")
        
        # Show personalization status
        if include_personalization:
            print(f"{Fore.CYAN}🎯 Personalization: Enabled{Style.RESET_ALL}")
            if include_rss:
                print(f"{Fore.CYAN}📡 RSS Feeds: Enabled{Style.RESET_ALL}")
            if include_web:
                print(f"{Fore.CYAN}🌐 Web Content: Enabled{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ Personalization: Disabled{Style.RESET_ALL}")
        
        if debug_mode:
            print(f"{Fore.MAGENTA}🐛 Debug Mode: Enabled - Content will be displayed in shell{Style.RESET_ALL}")

        results = {}
        with tqdm(total=len(self.generators), desc="Generating content",
                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            for chatter_type, generator in self.generators.items():
                try:
                    pbar.set_description(f"Generating {chatter_type}")
                    success = generator.process_and_deploy(
                        merge_existing=merge_existing,
                        include_personalization=include_personalization,
                        include_rss=include_rss,
                        include_web=include_web,
                        debug_mode=debug_mode,
                        max_entries=max_entries
                    )
                    results[chatter_type] = success
                    
                    if success:
                        pbar.set_postfix_str(f"{Fore.GREEN}✅{Style.RESET_ALL}")
                    else:
                        pbar.set_postfix_str(f"{Fore.RED}❌{Style.RESET_ALL}")
                        
                except Exception as e:
                    print(f"\n{Fore.RED}❌ Error generating {chatter_type}: {str(e)}{Style.RESET_ALL}")
                    results[chatter_type] = False
                    pbar.set_postfix_str(f"{Fore.RED}❌{Style.RESET_ALL}")
                
                pbar.update(1)
        
        return results

    def generate_prompts_only(self, file_types: list, max_entries: int, 
                           include_personalization: bool = True, include_rss: bool = True, 
                           include_web: bool = True) -> Dict[str, bool]:
        """Generate prompts for specific file types without sending to LLMs"""
        print(f"{Fore.BLUE}🎯 Generating prompts for specific files: {', '.join(file_types)}...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 Max entries per file: {max_entries}{Style.RESET_ALL}")
        
        # Show personalization status
        if include_personalization:
            print(f"{Fore.CYAN}🎯 Personalization: Enabled{Style.RESET_ALL}")
            if include_rss:
                print(f"{Fore.CYAN}📡 RSS Feeds: Enabled{Style.RESET_ALL}")
            if include_web:
                print(f"{Fore.CYAN}🌐 Web Content: Enabled{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ Personalization: Disabled{Style.RESET_ALL}")
        
        print(f"{Fore.MAGENTA}🐛 Prompt-Only Mode: Prompts will be saved to output directory{Style.RESET_ALL}")

        results = {}
        with tqdm(total=len(file_types), desc="Generating prompts",
                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            for file_type in file_types:
                if file_type not in self.generators:
                    print(f"{Fore.RED}❌ Unknown file type: {file_type}{Style.RESET_ALL}")
                    results[file_type] = False
                    pbar.update(1)
                    continue
                
                try:
                    pbar.set_description(f"Generating prompt for {file_type}")
                    generator = self.generators[file_type]
                    
                    success = generator.generate_prompt_only(
                        max_entries=max_entries,
                        include_personalization=include_personalization,
                        include_rss=include_rss,
                        include_web=include_web
                    )
                    results[file_type] = success
                    
                    if success:
                        pbar.set_postfix_str(f"{Fore.GREEN}✅{Style.RESET_ALL}")
                    else:
                        pbar.set_postfix_str(f"{Fore.RED}❌{Style.RESET_ALL}")
                        
                except Exception as e:
                    print(f"\n{Fore.RED}❌ Error generating prompt for {file_type}: {str(e)}{Style.RESET_ALL}")
                    results[file_type] = False
                    pbar.set_postfix_str(f"{Fore.RED}❌{Style.RESET_ALL}")
                
                pbar.update(1)
        
        return results

    def generate_all_prompts(self, include_personalization: bool = True, include_rss: bool = True,
                          include_web: bool = True, max_entries: int = 5) -> Dict[str, bool]:
        """Generate prompts for all chatter types without sending to LLMs"""
        print(f"{Fore.BLUE}🚀 Generating prompts for all chatter types...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 Max entries per file: {max_entries}{Style.RESET_ALL}")
        
        # Show personalization status
        if include_personalization:
            print(f"{Fore.CYAN}🎯 Personalization: Enabled{Style.RESET_ALL}")
            if include_rss:
                print(f"{Fore.CYAN}📡 RSS Feeds: Enabled{Style.RESET_ALL}")
            if include_web:
                print(f"{Fore.CYAN}🌐 Web Content: Enabled{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ Personalization: Disabled{Style.RESET_ALL}")
        
        print(f"{Fore.MAGENTA}🐛 Prompt-Only Mode: Prompts will be saved to output directory{Style.RESET_ALL}")

        results = {}
        with tqdm(total=len(self.generators), desc="Generating prompts",
                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            for chatter_type, generator in self.generators.items():
                try:
                    pbar.set_description(f"Generating prompt for {chatter_type}")
                    success = generator.generate_prompt_only(
                        max_entries=max_entries,
                        include_personalization=include_personalization,
                        include_rss=include_rss,
                        include_web=include_web
                    )
                    results[chatter_type] = success
                    
                    if success:
                        pbar.set_postfix_str(f"{Fore.GREEN}✅{Style.RESET_ALL}")
                    else:
                        pbar.set_postfix_str(f"{Fore.RED}❌{Style.RESET_ALL}")
                        
                except Exception as e:
                    print(f"\n{Fore.RED}❌ Error generating prompt for {chatter_type}: {str(e)}{Style.RESET_ALL}")
                    results[chatter_type] = False
                    pbar.set_postfix_str(f"{Fore.RED}❌{Style.RESET_ALL}")
                
                pbar.update(1)
        
        return results


def main():
    parser = argparse.ArgumentParser(description='EDCopilot Conversation Refresher')
    parser.add_argument('--keep-existing', action='store_true',
                       help='Keep existing content and merge with new content (default: replace entirely)')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (validate only)')
    parser.add_argument('--no-personalization', action='store_true',
                       help='Disable personalization context')
    parser.add_argument('--no-rss', action='store_true',
                       help='Disable RSS feed fetching')
    parser.add_argument('--no-web', action='store_true',
                       help='Disable web content fetching')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode - output generated content to shell')
    parser.add_argument('--files', nargs='+', choices=['chit_chat', 'space_chatter', 'crew_chatter', 'deep_space_chatter'],
                       help='Generate content for specific file types only')
    parser.add_argument('--max-entries', type=int, default=None,
                       help='Maximum number of entries to generate per file (default: from CONVERSATIONS_COUNT config)')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear RSS cache before running')
    parser.add_argument('--cache-info', action='store_true',
                       help='Show RSS cache information and exit')
    parser.add_argument('--prompt-only', action='store_true',
                       help='Generate and save prompts without sending to LLMs (enables debug mode)')
    
    args = parser.parse_args()
    
    # If prompt-only is specified, enable debug mode
    if args.prompt_only:
        args.debug = True
    
    updater = EDCopilotUpdater(debug_mode=args.debug)
    
    if args.cache_info:
        # Show cache information
        from src.utils.personalization import PersonalizationManager
        pm = PersonalizationManager()
        cache_info = pm.get_cache_info()
        
        print(f"{Fore.BLUE}📡 RSS Cache Information:{Style.RESET_ALL}")
        print(f"Cache Directory: {cache_info['cache_dir']}")
        print(f"Cache Duration: {cache_info['cache_duration_hours']:.1f} hours")
        print(f"Cached Feeds: {len(cache_info['cached_feeds'])}")
        
        if cache_info['cached_feeds']:
            print(f"\n{Fore.CYAN}Cached Feed Details:{Style.RESET_ALL}")
            for feed in cache_info['cached_feeds']:
                status = f"{Fore.GREEN}✅ Valid{Style.RESET_ALL}" if feed['valid'] else f"{Fore.RED}❌ Expired{Style.RESET_ALL}"
                age_info = f"{feed['age_hours']:.1f}h old" if feed['age_hours'] is not None else "Unknown age"
                print(f"  {feed['file']} - {status} ({age_info})")
        else:
            print(f"{Fore.YELLOW}No cached feeds found{Style.RESET_ALL}")
        
        return 0
    
    if args.test:
        success = updater.validate_setup()
        return 0 if success else 1
    else:
        # Clear cache if requested
        if args.clear_cache:
            from src.utils.personalization import PersonalizationManager
            pm = PersonalizationManager()
            pm.clear_rss_cache()
            print(f"{Fore.YELLOW}🗑️ RSS cache cleared{Style.RESET_ALL}")
        
        merge_existing = args.keep_existing
        include_personalization = not args.no_personalization
        include_rss = not args.no_rss
        include_web = not args.no_web
        debug_mode = args.debug
        specific_files = args.files
        
        # Use CONVERSATIONS_COUNT from config if not specified and not in debug mode
        if args.max_entries is not None:
            max_entries = args.max_entries
        elif debug_mode:
            max_entries = 5  # Default for debug mode
        else:
            max_entries = Config.CONVERSATIONS_COUNT  # Use config value for normal operation
        
        success = updater.run(
            merge_existing=merge_existing,
            include_personalization=include_personalization,
            include_rss=include_rss,
            include_web=include_web,
            debug_mode=debug_mode,
            specific_files=specific_files,
            max_entries=max_entries,
            prompt_only=args.prompt_only
        )
        return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
