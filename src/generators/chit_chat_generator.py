"""
ChitChat Generator module for EDCopilot Chit Chat Updater
Generates general casual conversation content
"""

from src.generators.base_generator import BaseGenerator

class ChitChatGenerator(BaseGenerator):
    """Generator for general chit chat content"""
    
    def __init__(self, debug_mode: bool = False):
        super().__init__(
            chatter_type="chit_chat",
            output_file="EDCoPilot.ChitChat.Custom.txt",
            debug_mode=debug_mode
        )
    
    def _build_prompt(self, num_entries: int) -> str:
        """Build the prompt for chit chat content generation"""
        return f"""
You are generating casual chit chat phrases for Elite Dangerous EDCopilot. 
The Chit Chat feature enables your CoPilot to say random phrases after a period of inactivity.

Generate exactly {num_entries} casual chit chat phrases that are:

- Simple, standalone phrases spoken by EDCopilot
- Can include tokens that EDCopilot will replace with game data:
  - <cmdrname> - Commander's name
  - <starsystem> - Current star system
  - <station> - Current station name
  - <ship> - Ship name
  - <credits> - Current credits

## Personalization Context

**Facts:**
{{data}}

**Recent News:**
{{rss_summary}}

Examples of proper chit chat format:
- Hello <cmdrname>, how can I assist you today?
- We are currently in the <starsystem> system.
- Listed to a great Galnet article last night.

**PROBABILITY GUIDELINES:**
- Only {{personalization_chance}}% of phrases should include personal references (commander name, squadron, fleet carrier)
- Only {{rss_chance}}% of phrases should reference recent news
- Most phrases ({{100-personalization_chance}}%) should be generic and not personalized
- Mix generic and personalized content appropriately

Generate phrases that are defined by the following guidelines:
- Natural and conversational in tone
- (REQUIRED) One phrase per line
- Include portions of recent news
- Include occasional tokens for personalization
{{themes}}
{{conversation_styles}}

Format the output as plain text with one phrase per line.
"""
