"""
Base Generator module for EDCopilot Chit Chat Updater
Provides common functionality for all content generators
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Optional

from src.utils.api_client import APIClient
from src.utils.file_manager import FileManager
from src.config import Config

logger = logging.getLogger(__name__)

class BaseGenerator(ABC):
    """Abstract base class for content generators"""
    
    def __init__(self, chatter_type: str, output_file: str, debug_mode: bool = False):
        self.chatter_type = chatter_type
        self.output_file = output_file
        self.debug_mode = debug_mode
        self.api_client = APIClient()
        self.file_manager = FileManager(debug_mode=debug_mode)
    
    def validate_setup(self) -> bool:
        """Validate the generator setup"""
        try:
            # Check if API client is properly configured
            if not self.api_client:
                logger.error(f"❌ API client not initialized for {self.chatter_type}")
                return False
            
            # Check if file manager is properly configured
            if not self.file_manager:
                logger.error(f"❌ File manager not initialized for {self.chatter_type}")
                return False
            
            logger.info(f"✅ {self.chatter_type} generator setup validated")
            return True
            
        except Exception as e:
            logger.error(f"❌ {self.chatter_type} generator validation failed: {str(e)}")
            return False
    
    def generate_content(self, num_entries: int = 50, include_personalization: bool = True,
                        include_rss: bool = True, include_web: bool = True, debug_mode: bool = False) -> Optional[str]:
        """Generate content using the API client"""
        logger.info(f"🚀 Starting content generation for {self.chatter_type}")
        base_prompt = self._build_prompt(num_entries)
        
        # Build enhanced prompt with personalization if enabled
        if include_personalization:
            personalization_context = self.api_client.personalization_manager.get_personalization_context(
                include_rss=include_rss, include_web=include_web)
            if personalization_context:
                enhanced_prompt = self._build_enhanced_prompt(base_prompt, personalization_context)
                final_prompt = enhanced_prompt
            else:
                final_prompt = base_prompt
        else:
            final_prompt = base_prompt
        
        # Get the enhanced prompt with personalization for debug logging
        if debug_mode:
            if include_personalization and personalization_context:
                # Create a clean debug version without verbose RSS content
                debug_prompt = self._create_debug_prompt(personalization_context, base_prompt)
                logger.info(f"🐛 ENHANCED PROMPT FOR {self.chatter_type.upper()}:")
                logger.info(f"🐛 {debug_prompt}")
                logger.info(f"🐛 FULL PERSONALIZATION CONTEXT LENGTH: {len(personalization_context)} characters")
                logger.info(f"🐛 FULL ENHANCED PROMPT LENGTH: {len(final_prompt)} characters")
                logger.info(f"🐛 PERSONALIZATION SECTIONS FOUND: {list(self.api_client.personalization_manager.context_data.keys())}")
                # Uncomment the next line to see the full personalization context in debug logs
                # logger.info(f"🐛 FULL PERSONALIZATION CONTEXT: {personalization_context}")
            else:
                logger.info(f"🐛 BASIC PROMPT FOR {self.chatter_type.upper()}:")
                logger.info(f"🐛 {base_prompt}")
        
        content = self.api_client.generate_content(final_prompt, self.chatter_type,
                                                  include_personalization=False,  # Already included in prompt
                                                  include_rss=False,  # Already included in prompt
                                                  include_web=False)  # Already included in prompt
        if content:
            logger.info(f"✅ Generated {len(content)} characters for {self.chatter_type}")
            return content
        else:
            logger.error(f"❌ Failed to generate content for {self.chatter_type}")
            return None
    
    def process_and_deploy(self, merge_existing: bool = False, include_personalization: bool = True,
                          include_rss: bool = True, include_web: bool = True, debug_mode: bool = False,
                          max_entries: int = 5) -> bool:
        """Process and deploy the generated content"""
        logger.info(f"🔄 Processing {self.chatter_type}")
        
        # Generate content with the specified max_entries
        new_content = self.generate_content(num_entries=max_entries,
                                           include_personalization=include_personalization,
                                           include_rss=include_rss,
                                           include_web=include_web,
                                           debug_mode=debug_mode)
        
        if not new_content:
            return False
        
        # If debug mode is enabled, output the content to shell
        if debug_mode:
            self._output_debug_content(new_content)
        
        # Process the content
        processed_content = self._process_content(new_content)
        if not processed_content:
            logger.error(f"❌ Failed to process content for {self.chatter_type}")
            return False
        
        # Deploy the content
        success = self._deploy_content(processed_content, merge_existing)
        if success:
            logger.info(f"✅ Successfully deployed {self.chatter_type}")
        else:
            logger.error(f"❌ Failed to deploy {self.chatter_type}")
        
        return success
    
    def _output_debug_content(self, content: str):
        """Output generated content to shell in debug mode"""
        from colorama import Fore, Style
        
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}🐛 DEBUG OUTPUT - {self.chatter_type.upper()}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(content)
        print(f"{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}END DEBUG OUTPUT - {self.chatter_type.upper()}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")
    
    def _process_content(self, content: str) -> Optional[str]:
        """Process the generated content"""
        try:
            # Basic content processing - can be overridden by subclasses
            processed = content.strip()
            if not processed:
                logger.warning(f"⚠️ Empty content generated for {self.chatter_type}")
                return None
            
            # Clean up common formatting issues
            processed = self._cleanup_content(processed)
            
            # Sanity check and remove incomplete conversations
            processed = self._sanity_check_conversations(processed)
            
            logger.info(f"✅ Processed content for {self.chatter_type}")
            return processed
            
        except Exception as e:
            logger.error(f"❌ Error processing content for {self.chatter_type}: {str(e)}")
            return None
    
    def _create_debug_prompt(self, personalization_context: str, prompt: str) -> str:
        """Create a clean debug version of the prompt without verbose RSS content"""
        import re
        
        # Extract personal context (Specific Data, Quick Notes) but skip RSS content
        lines = personalization_context.split('\n')
        clean_lines = []
        
        # Keep the header and personal data sections
        keep_sections = ['## Personal Context:', '### Data:', '### Conversation Styles:']
        skip_sections = ['## Recent News and Updates:', '### From', '## Web Content References:']
        
        in_keep_section = False
        in_skip_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if we're entering a section to keep
            if any(section in line for section in keep_sections):
                in_keep_section = True
                in_skip_section = False
                clean_lines.append(line)
                continue
                
            # Check if we're entering a section to skip
            if any(section in line for section in skip_sections):
                in_keep_section = False
                in_skip_section = True
                continue
                
            # If we're in a keep section, add the line
            if in_keep_section and not in_skip_section:
                clean_lines.append(line)
                
            # If we hit another section header, stop keeping
            if line.startswith('##') and not any(section in line for section in keep_sections):
                in_keep_section = False
                in_skip_section = False
        
        # Create the clean personalization context
        clean_personalization = '\n'.join(clean_lines)
        
        # Add a note about RSS content being included
        clean_personalization += '\n\n[RSS and Web Content Included - Not Shown in Debug]'
        
        # Combine with the prompt
        debug_prompt = f"{clean_personalization}\n\n{prompt}"
        
        return debug_prompt
    
    def _build_enhanced_prompt(self, base_prompt: str, personalization_context: str = None) -> str:
        """Build an enhanced prompt that integrates personalization and RSS content into the generation instructions"""
        if not personalization_context:
            return base_prompt
        
        # Extract key personalization elements
        personal_data = self._extract_personalization_data(personalization_context)
        
        # Create enhanced prompt with integrated personalization
        enhanced_prompt = f"""
{base_prompt}

## Personalization Guidelines:
{personal_data['specific_data']}

## Content Style and Preferences:
{personal_data['quick_notes']}

## Recent Context and News:
{personal_data['rss_summary']}

## Generation Instructions:
When generating conversations, please follow these probability guidelines:

**Context Tags (Conditionals):**
- Only {Config.CONVERSATIONS_CHANCE_CONDITIONALS}% of conversations should include context tags
- When context tags are used, they should only appear on the first line of the conversation
- Valid context tags: (not-station), (not-planet), (not-deep-space)
- Most conversations (90%) should NOT have context tags

**Personalization References:**
- Only {Config.CONVERSATIONS_CHANCE_PERSONALIZATION}% of conversations should include personal references
- When used, naturally incorporate: commander's name ({personal_data['commander_name']}), squadron ({personal_data['squadron_name']}), fleet carrier ({personal_data['fleet_carrier']})
- Most conversations (75%) should be generic and not personalized

**RSS Feed References:**
- Only {Config.CONVERSATIONS_CHANCE_RSS}% of conversations should reference recent news/events
- When used, naturally incorporate recent news and events from the RSS feeds
- Most conversations (85%) should NOT reference current events

**General Guidelines:**
- Use the specified theme and style preferences
- Follow the content guidelines and avoid topics that should be avoided
- Ensure conversations feel natural and varied
- Mix generic and personalized content appropriately
"""
        
        return enhanced_prompt
    
    def _extract_personalization_data(self, personalization_context: str) -> dict:
        """Extract key personalization data from the context"""
        import re
        
        data = {
            'commander_name': 'Commander',
            'squadron_name': 'the squadron',
            'fleet_carrier': 'the fleet carrier',
            'specific_data': 'No specific data available',
            'quick_notes': 'No specific preferences noted',
            'rss_summary': 'Recent news and events are available for context'
        }
        
        lines = personalization_context.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if '### Specific Data:' in line:
                current_section = 'specific_data'
                data['specific_data'] = []
                continue
            elif '### Quick Notes:' in line:
                current_section = 'quick_notes'
                data['quick_notes'] = []
                continue
            elif '## Recent News and Updates:' in line:
                current_section = 'rss'
                data['rss_summary'] = []
                continue
            
            # Extract commander name
            if 'Commander Name:' in line:
                match = re.search(r'Commander Name:\s*(.+)', line)
                if match:
                    data['commander_name'] = match.group(1).strip()
            
            # Extract squadron name
            elif 'Squadron Name:' in line:
                match = re.search(r'Squadron Name:\s*(.+)', line)
                if match:
                    data['squadron_name'] = match.group(1).strip()
            
            # Extract fleet carrier name
            elif 'Fleet Carrier Name:' in line:
                match = re.search(r'Fleet Carrier Name:\s*(.+)', line)
                if match:
                    data['fleet_carrier'] = match.group(1).strip()
            
            # Collect section content
            elif current_section and line.startswith('-'):
                if current_section == 'specific_data':
                    data['specific_data'].append(line)
                elif current_section == 'quick_notes':
                    data['quick_notes'].append(line)
                elif current_section == 'rss':
                    data['rss_summary'].append(line)
        
        # Convert lists to strings
        for key in ['specific_data', 'quick_notes', 'rss_summary']:
            if isinstance(data[key], list):
                data[key] = '\n'.join(data[key]) if data[key] else f'No {key.replace("_", " ")} available'
        
        return data
    
    def _cleanup_content(self, content: str) -> str:
        """Clean up common formatting issues in generated content"""
        import re
        
        # Fix double angle brackets in speaker tags: [<<Speaker>] -> [<Speaker>]
        content = re.sub(r'\[<<([^>]+)>\]', r'[<\1>]', content)
        
        # Fix any remaining double angle brackets in context tags
        content = re.sub(r'\(<<([^>]+)>\)', r'(<\1>)', content)
        
        # Fix non-standard context tags
        content = self._fix_context_tags(content)
        
        # Fix speaker tags for crew chatter
        content = self._fix_speaker_tags(content)
        
        # Normalize line endings to \n
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Clean up excessive blank lines (more than 2 consecutive)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Fix multiple spaces within lines (but preserve line breaks)
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Fix multiple spaces within the line
            cleaned_line = re.sub(r' +', ' ', line.strip())
            if cleaned_line:  # Only add non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join lines back together
        content = '\n'.join(cleaned_lines)
        
        return content
    
    def _fix_context_tags(self, content: str) -> str:
        """Fix non-standard context tags to use proper format"""
        import re
        
        # Define valid context tags for each chatter type (official EDCopilot tags only)
        valid_tags = {
            'chit_chat': [],  # Chit chat doesn't use context tags
            'crew_chatter': [
                '(not-station)', '(not-planet)', '(not-deep-space)'
            ],
            'space_chatter': [
                '(not-station)', '(not-planet)', '(not-deep-space)'
            ],
            'deep_space_chatter': [
                '(not-station)', '(not-planet)', '(not-deep-space)'
            ]
        }
        
        # Get valid tags for this chatter type
        valid_tags_for_type = valid_tags.get(self.chatter_type, [])
        
        # If this is chit_chat, remove any context tags
        if self.chatter_type == 'chit_chat':
            content = re.sub(r'\s*\([^)]+\)\s*', ' ', content)
            return content
        
        # Fix common non-standard tags to official EDCopilot tags
        tag_fixes = {
            r'\(not-in-station\)': '(not-station)',
            r'\(not-on-planet\)': '(not-planet)',
            r'\(not-in-deep-space\)': '(not-deep-space)',
            r'\(deep-space\)': '(not-deep-space)',  # Convert deep-space to not-deep-space
            r'\(exploring\)': '(not-station)',  # Convert exploring to not-station
            r'\(in-combat\)': '(not-station)',  # Convert in-combat to not-station
            r'\(trading\)': '(not-station)',  # Convert trading to not-station
            r'\(mining\)': '(not-station)',  # Convert mining to not-station
            r'\(fuel-low\)': '(not-station)',  # Convert fuel-low to not-station
            r'\(damage\)': '(not-station)',  # Convert damage to not-station
            r'\(near-nebula\)': '(not-station)',  # Convert near-nebula to not-station
            r'\(near-black-hole\)': '(not-station)',  # Convert near-black-hole to not-station
            r'\(near-neutron-star\)': '(not-station)',  # Convert near-neutron-star to not-station
            r'\(asteroid-field\)': '(not-station)',  # Convert asteroid-field to not-station
            r'\(unknown-region\)': '(not-station)',  # Convert unknown-region to not-station
            r'\(distant-system\)': '(not-station)',  # Convert distant-system to not-station
            r'\(void\)': '(not-station)',  # Convert void to not-station
            r'\(anomaly\)': '(not-station)',  # Convert anomaly to not-station
        }
        
        for wrong_tag, correct_tag in tag_fixes.items():
            content = re.sub(wrong_tag, correct_tag, content, flags=re.IGNORECASE)
        
        # Process context tags - only apply to first line of each conversation
        lines = content.split('\n')
        cleaned_lines = []
        in_example = False
        first_line_in_example = True
        
        for line in lines:
            if line.strip() == '[example]':
                in_example = True
                first_line_in_example = True
                cleaned_lines.append(line)
                continue
            elif line.strip() == '[/example]':
                in_example = False
                first_line_in_example = False
                cleaned_lines.append(line)
                continue
            
            if in_example and line.strip().startswith('[<') and ']' in line:
                # This is a speaker line within an example
                if first_line_in_example:
                    # First line of conversation - check and fix context tags
                    context_tags = re.findall(r'\([^)]+\)', line)
                    valid_context_tags = []
                    
                    for tag in context_tags:
                        if tag in valid_tags_for_type:
                            valid_context_tags.append(tag)
                        else:
                            logger.warning(f"⚠️ Removed invalid context tag '{tag}' from {self.chatter_type}")
                    
                    # Reconstruct the line with only valid context tags (or none if empty)
                    line_without_tags = re.sub(r'\s*\([^)]+\)\s*', ' ', line)
                    if valid_context_tags:
                        # Add back valid context tags
                        speaker_end = line_without_tags.find(']') + 1
                        before_speaker = line_without_tags[:speaker_end]
                        after_speaker = line_without_tags[speaker_end:].strip()
                        line = f"{before_speaker} {' '.join(valid_context_tags)} {after_speaker}"
                    # If no valid context tags, leave the line without any (context tags are optional)
                    
                    first_line_in_example = False
                else:
                    # Not the first line - remove any context tags
                    line = re.sub(r'\s*\([^)]+\)\s*', ' ', line)
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _fix_speaker_tags(self, content: str) -> str:
        """Fix speaker tags to use proper EDCopilot format"""
        import re
        
        # Define valid speaker tags for each chatter type
        valid_speakers = {
            'chit_chat': [],  # Chit chat doesn't use speaker tags
            'crew_chatter': [
                '[<Number1>]', '[<Science>]', '[<Helm>]', '[<Operations>]', '[<Engineering>]', 
                '[<Comms>]', '[<EDCoPilot>]', '[<Crew:Medical>]', '[<Crew:Tactical>]', 
                '[<Crew:Maintenance>]', '[<Crew:Security>]'
            ],
            'space_chatter': [
                '[<Helm>]', '[<EDCoPilot>]', '[<Science>]', '[<Operations>]', '[<Tactical>]', '[<Communications>]'
            ],
            'deep_space_chatter': [
                '[<Number1>]', '[<Science>]', '[<Helm>]', '[<Operations>]', '[<Engineering>]', 
                '[<Comms>]', '[<EDCoPilot>]', '[<Crew:Medical>]', '[<Crew:Tactical>]', 
                '[<Crew:Maintenance>]', '[<Crew:Security>]', '[<Ship1>]', '[<Ship2>]', '[<Ship3>]', '[<Ship4>]'
            ]
        }
        
        # Get valid speakers for this chatter type
        valid_speakers_for_type = valid_speakers.get(self.chatter_type, [])
        
        # If this is chit_chat, no speaker tags needed
        if self.chatter_type == 'chit_chat':
            return content
        
        # Fix common non-standard speaker tags for crew chatter and deep space chatter
        if self.chatter_type in ['crew_chatter', 'deep_space_chatter']:
            speaker_fixes = {
                r'\[<Medical>\]': '[<Crew:Medical>]',
                r'\[<Tactical>\]': '[<Crew:Tactical>]',
                r'\[<Communications>\]': '[<Comms>]',
                r'\[<Comm>\]': '[<Comms>]',
                r'\[<Commander>\]': '[<Number1>]',
                r'\[<Captain>\]': '[<Number1>]',
                r'\[<Crew>\]': '[<Number1>]',
            }
            
            for wrong_speaker, correct_speaker in speaker_fixes.items():
                content = re.sub(wrong_speaker, correct_speaker, content, flags=re.IGNORECASE)
        
        # Process lines and fix invalid speaker tags
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.strip().startswith('[<') and ']' in line:
                # This is a speaker line, check if it's valid
                speaker_match = re.match(r'^(\[<[^>]+>\])\s*', line)
                if speaker_match:
                    speaker_tag = speaker_match.group(1)
                    if speaker_tag not in valid_speakers_for_type:
                        # Replace with a default speaker
                        if self.chatter_type == 'crew_chatter':
                            default_speaker = '[<Number1>]'
                        else:
                            default_speaker = valid_speakers_for_type[0] if valid_speakers_for_type else '[<EDCoPilot>]'
                        
                        line = re.sub(r'^\[<[^>]+>\]', default_speaker, line)
                        logger.warning(f"⚠️ Replaced invalid speaker tag with '{default_speaker}' in {self.chatter_type}")
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _sanity_check_conversations(self, content: str) -> str:
        """Sanity check and remove incomplete conversations"""
        import re
        
        # Split content into lines
        lines = content.split('\n')
        cleaned_lines = []
        in_example = False
        example_start_line = -1
        example_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for start of example
            if line == '[example]':
                in_example = True
                example_start_line = i
                example_lines = [line]
                continue
            
            # If we're in an example, collect lines
            if in_example:
                example_lines.append(line)
                
                # Check for end of example
                if line == '[/example]':
                    # Validate this example
                    if self._is_valid_example(example_lines):
                        cleaned_lines.extend(example_lines)
                    else:
                        logger.warning(f"⚠️ Removed incomplete conversation starting at line {example_start_line + 1}")
                    in_example = False
                    example_start_line = -1
                    example_lines = []
                continue
            
            # If we're not in an example, add the line
            if not in_example:
                cleaned_lines.append(line)
        
        # Handle any incomplete example at the end
        if in_example:
            logger.warning(f"⚠️ Removed incomplete conversation at end of content")
        
        return '\n'.join(cleaned_lines)
    
    def _is_valid_example(self, example_lines: list) -> bool:
        """Check if an example conversation is complete and valid"""
        if len(example_lines) < 3:  # Need at least [example], one line of content, and [/example]
            return False
        
        # Check for proper start and end tags
        if example_lines[0] != '[example]' or example_lines[-1] != '[/example]':
            return False
        
        # Check that we have at least one line of actual content (not just tags)
        content_lines = example_lines[1:-1]  # Exclude start and end tags
        has_content = False
        
        for line in content_lines:
            line = line.strip()
            # Check for speaker lines with content: [<Speaker>] (context) message
            if re.match(r'^\[<[^>]+>\].*', line) and len(line) > 10:  # Has speaker tag and content
                has_content = True
                break
        
        if not has_content:
            return False
        
        # Check for incomplete speaker lines (lines that start with [<Speaker>] but have no content)
        for line in content_lines:
            line = line.strip()
            if re.match(r'^\[<[^>]+>\]\s*$', line):  # [<Speaker>] with no content
                return False
        
        return True
    
    def _deploy_content(self, content: str, merge_existing: bool) -> bool:
        """Deploy the processed content to the output file"""
        try:
            # Get the correct output path based on debug mode
            output_path = self.file_manager.get_output_path(self.output_file)
            
            if merge_existing:
                success = self.file_manager.merge_content(str(output_path), content)
            else:
                success = self.file_manager.write_content(str(output_path), content)
            
            if success:
                logger.info(f"✅ Content deployed to {output_path}")
                return True
            else:
                logger.error(f"❌ Failed to deploy content to {output_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deploying content for {self.chatter_type}: {str(e)}")
            return False
    
    @abstractmethod
    def _build_prompt(self, num_entries: int) -> str:
        """Build the prompt for content generation - must be implemented by subclasses"""
        pass
