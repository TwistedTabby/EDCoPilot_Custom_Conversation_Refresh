"""
CrewChatter Generator module for EDCopilot Chit Chat Updater
Generates crew member interaction content
"""

from src.generators.base_generator import BaseGenerator

class CrewChatterGenerator(BaseGenerator):
    """Generator for crew interaction chatter content"""
    
    def __init__(self, debug_mode: bool = False):
        super().__init__(
            chatter_type="crew_chatter",
            output_file="EDCoPilot.CrewChatter.Custom.txt",
            debug_mode=debug_mode
        )
    
    def _build_prompt(self, num_entries: int) -> str:
        """Build the prompt for crew chatter content generation"""
        return f"""
You are generating crew interaction conversation content for Elite Dangerous EDCopilot. 
While onboard our ship, we may hear our crew talking among themselves . They may be discussing ship operations, making small talk, or talking about places of interest in our vicinity.

Generate exactly {num_entries} crew interaction conversation examples that follow the EDCopilot format:

## Personalization Context

**Facts:**
{{data}}

**Recent News:**
{{rss_summary}}

IMPORTANT: Vary the conversation lengths naturally. Aim for this distribution:
- 40% short conversations (1-2 lines of dialogue)
- 35% medium conversations (3-4 lines of dialogue) 
- 20% longer conversations (5-6 lines of dialogue)
- 5% extended conversations (7+ lines of dialogue)

Available speakers:
- [<Number1>] - First crew member
- [<Science>] - Scientific observations and analysis
- [<Helm>] - Navigation and piloting
- [<Operations>] - General operations and status
- [<Engineering>] - Ship systems and maintenance
- [<Comms>] - Communications and external contact
- [<EDCoPilot>] - The ship's computer (AI assistant responses)
- [<Crew:ROLE>] - If used, create a role name to replace ROLE

Context tags to use (OPTIONAL - only on the first line of each conversation and can have multiple tags):
- (not-station) - Will not pick this conversation if you are currently at/around a station
- (not-planet) - Will not pick this conversation if you are currently on or approaching a planet
- (not-deep-space) - Will not pick this conversation if you are currently out in deep space (> 5000 ly from Sol and Colonia)

**PROBABILITY GUIDELINES:**
- Only {{conditionals_chance}}% of conversations should include context tags
- Most conversations ({{100-conditionals_chance}}%) should NOT have context tags
- When context tags are used, they should only appear on the first line
- Only {{personalization_chance}}% of conversations should include personal references
- Only {{rss_chance}}% of conversations should reference recent news/events

Examples of different conversation lengths:

SHORT (1-2 lines):
[example]
[<Engineering>] (not-station) (not-planet) The power distribution is running smoothly today.
[<EDCoPilot>] Affirmative, all systems are operating within optimal parameters.
[/example]

MEDIUM (3-4 lines):
[example]
[<Crew:Medical>] (not-station) I've completed the routine health scans for the crew.
[<EDCoPilot>] Excellent, all crew members are showing normal vital signs.
[<Operations>] The medical bay supplies are well-stocked for our current mission.
[<Crew:Medical>] We're prepared for any emergency situations that might arise.
[/example]

LONGER (5-6 lines):
[example]
[<Helm>] (not-station) (not-planet) The navigation systems are detecting some unusual stellar phenomena ahead.
[<Science>] Those readings suggest we're approaching a region of intense gravitational lensing.
[<EDCoPilot>] I recommend we adjust our course to avoid potential navigation hazards.
[<Crew:Tactical>] The tactical systems are ready to respond to any threats in the area.
[<Operations>] All crew stations are prepared for the course correction.
[<Helm>] Executing the course adjustment now, Commander.
[/example]

Generate conversations that are:
- Focused on ship crew interactions and operations
- Include appropriate speaker tags and context tags
- Engaging for space simulation enthusiasts
- Vary naturally in length (short conversations should be more common)
- Each conversation wrapped in [example]...[/example] tags
- Ensure conversations feel natural and varied
- Mix generic and personalized content appropriately
- Incorporate recent news and events naturally when relevant
- Avoid conversations about present events that may or may not be true. (e.g. "The <station> docking bay is quite busy today.")
- To talk about things that ship crew would talk about specific to their role use past tense like "Remember when we saw that black hole?"
{{themes}}
{{conversation_styles}}

Format: 
[example]
[<Speaker>] (condition-tags) Message content
[<Speaker>] Response content
[/example]
"""
