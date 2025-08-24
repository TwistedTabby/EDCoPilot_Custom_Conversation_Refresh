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
This content will be used for general chit chat where EDCopilot speaks directly to the commander.

Generate exactly {num_entries} casual chit chat phrases that are:

- Simple, standalone phrases spoken by EDCopilot
- NO speaker tags, NO context tags - just the phrases themselves
- Can include tokens that EDCopilot will replace with game data:
  - <cmdrname> - Commander's name
  - <starsystem> - Current star system
  - <station> - Current station name
  - <ship> - Ship name
  - <credits> - Current credits

## Personalization Context

**Data:**
{{data}}

**Themes:**
{{themes}}

**Conversation Styles:**
{{conversation_styles}}

**Recent News:**
{{rss_summary}}

Examples of proper chit chat format:
- Hello <cmdrname>, how can I assist you today?
- We are currently in the <starsystem> system.
- Your <ship> is looking good, Commander.
- I hope you're having a productive day, <cmdrname>.
- The <station> docking bay is quite busy today.

Generate phrases that are:
- Light-hearted and friendly
- Appropriate for casual conversation
- Natural and conversational in tone
- One phrase per line
- No numbering or bullet points
- Include occasional tokens for personalization

**PROBABILITY GUIDELINES:**
- Only {{personalization_chance}}% of phrases should include personal references (commander name, squadron, fleet carrier)
- Only {{rss_chance}}% of phrases should reference recent news/events
- Most phrases ({{100-personalization_chance}}%) should be generic and not personalized
- Mix generic and personalized content appropriately

Format the output as plain text with one phrase per line.
"""
