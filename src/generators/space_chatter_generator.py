"""
SpaceChatter Generator module for EDCopilot Chit Chat Updater
Generates space-themed conversation content
"""

from src.generators.base_generator import BaseGenerator

class SpaceChatterGenerator(BaseGenerator):
    """Generator for space-themed chatter content"""
    
    def __init__(self, debug_mode: bool = False):
        super().__init__(
            chatter_type="space_chatter",
            output_file="EDCoPilot.SpaceChatter.Custom.txt",
            debug_mode=debug_mode
        )
    
    def _build_prompt(self, num_entries: int) -> str:
        """Build the prompt for space chatter content generation"""
        return f"""
You are generating space-themed conversation content for Elite Dangerous EDCopilot. 
While we are waiting to dock at a station we can hear radio transmissions from other ships around us who are either requesting docking, waiting to dock, or are inside the station preparing to leave. Their requests may be replied to by the Control Tower in the station.

Generate exactly {num_entries} space-themed conversation examples that follow the EDCopilot format:

## Personalization Context

**Data:**
{{data}}

**Recent News:**
{{rss_summary}}

IMPORTANT: Vary the conversation lengths naturally. Aim for this distribution:
- 40% short conversations (1-2 lines of dialogue)
- 35% medium conversations (3-4 lines of dialogue) 
- 20% longer conversations (5-6 lines of dialogue)
- 5% extended conversations (7+ lines of dialogue)

Available speakers:
- [<Helm>] - Navigation and piloting observations
- [<EDCoPilot>] - AI assistant responses about space
- [<Science>] - Scientific observations and analysis
- [<Operations>] - General space observations
- [<Tactical>] - Space hazards and navigation warnings
- [<Communications>] - Communications about space phenomena
- [<Crew:ROLE>] - If used, create a role name to replace ROLE

Condition tags to use (OPTIONAL - only on the first line of each conversation and can include multiple conditions):
- (not-station) - Will not pick this conversation if you are currently at/around a station
- (not-planet) - Will not pick this conversation if you are currently on or approaching a planet
- (not-deep-space) - Will not pick this conversation if you are currently out in deep space (> 5000 ly from Sol and Colonia)

IMPORTANT: Context tags are optional and should only be used on the first line of each conversation when relevant. Use multiple tags when appropriate (e.g., (not-station) (not-planet) for conversations away from both stations and planets).

**PROBABILITY GUIDELINES:**
- Only {{conditionals_chance}}% of conversations should include context tags
- Most conversations ({{100-conditionals_chance}}%) should NOT have context tags
- When context tags are used, they should only appear on the first line
- Only {{personalization_chance}}% of conversations should include personal references
- Only {{rss_chance}}% of conversations should reference recent news/events

Examples of different conversation lengths:

SHORT (1-2 lines):
[example]
[<Science>] (not-station) (not-planet) That's a beautiful binary star system.
[<EDCoPilot>] Indeed, Commander. The gravitational dance between those stars is fascinating.
[/example]

MEDIUM (3-4 lines):
[example]
[<Helm>] (not-station) The colors in this nebula are absolutely breathtaking!
[<Science>] Those colors indicate different elements being ionized by nearby stars.
[<Operations>] We're detecting unusual radiation patterns from that distant star cluster.
[<EDCoPilot>] The radiation suggests recent supernova activity in that region.
[/example]

LONGER (5-6 lines):
[example]
[<Science>] Did you know that Betelgeuse is expected to go supernova within the next 100,000 years?
[<EDCoPilot>] That's correct, Commander. Betelgeuse is a red supergiant star in the constellation Orion.
[<Operations>] When it does go supernova, it will be visible even during the day.
[<Science>] The explosion will release elements like carbon, oxygen, and iron into space.
[<Helm>] It's amazing how the death of one star creates the building blocks for new ones.
[<EDCoPilot>] The cycle of stellar birth and death is fundamental to cosmic evolution.
[/example]

Generate conversations that are:
- Focused on ship crew interactions and operations
- Include appropriate speaker tags and context tags
- Ensure conversations feel natural and varied
- Mix generic and personalized content appropriately
- Each conversation wrapped in [example]...[/example] tags
- Incorporate recent news and events naturally when relevant
- Avoid conversations about present events that may or may not be true. (e.g. "The <station> docking bay is quite busy today.")
- To talk about things that ship crew would talk about specific to their role use past tense like "Remember when we saw that black hole?"
{{themes}}
{{conversation_styles}}

Format: 
[example]
[<Speaker>] (context-tags) Message content
[<Speaker>] (context-tags) Response content
[/example]
"""
