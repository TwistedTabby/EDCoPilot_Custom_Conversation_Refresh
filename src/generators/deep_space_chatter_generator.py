"""
DeepSpaceChatter Generator module for EDCopilot Chit Chat Updater
Generates deep space exploration conversation content
"""

from src.generators.base_generator import BaseGenerator

class DeepSpaceChatterGenerator(BaseGenerator):
    """Generator for deep space exploration chatter content"""
    
    def __init__(self, debug_mode: bool = False):
        super().__init__(
            chatter_type="deep_space_chatter",
            output_file="EDCoPilot.DeepSpaceChatter.Custom.txt",
            debug_mode=debug_mode
        )
    
    def _build_prompt(self, num_entries: int) -> str:
        """Build the prompt for deep space chatter content generation"""
        return f"""
You are generating deep space exploration conversation content for Elite Dangerous EDCopilot. 
This content will be used for conversations specifically about deep space exploration, mysteries, and encounters far from civilized space.

Generate exactly {num_entries} deep space exploration conversation examples that follow the EDCopilot format:

## Personalization Context

**Data:**
{{data}}

**Themes:**
{{themes}}

**Conversation Styles:**
{{conversation_styles}}

**Recent News:**
{{rss_summary}}

IMPORTANT: Vary the conversation lengths naturally. Aim for this distribution:
- 40% short conversations (1-2 lines of dialogue)
- 35% medium conversations (3-4 lines of dialogue) 
- 20% longer conversations (5-6 lines of dialogue)
- 5% extended conversations (7+ lines of dialogue)

Each conversation should be wrapped in [example]...[/example] tags.

Format: 
[example]
[<Speaker>] (context-tags) Message content
[<Speaker>] (context-tags) Response content
[/example]

Available speakers:
- [<Number1>] - First crew member
- [<Science>] - Scientific observations and analysis
- [<Helm>] - Navigation and piloting
- [<Operations>] - General operations and status
- [<Engineering>] - Ship systems and maintenance
- [<Comms>] - Communications and external contact
- [<EDCoPilot>] - The ship's computer (AI assistant responses)
- [<Crew:Medical>] - Medical crew member
- [<Crew:Tactical>] - Tactical crew member
- [<Crew:Maintenance>] - Maintenance crew member
- [<Crew:Security>] - Security crew member
- [<Ship1>] - First ship encounter
- [<Ship2>] - Second ship encounter
- [<Ship3>] - Third ship encounter
- [<Ship4>] - Fourth ship encounter

Context tags to use (OPTIONAL - only on the first line of each conversation):
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
[<Science>] (not-station) (not-planet) The stellar density out here is absolutely incredible.
[<EDCoPilot>] Indeed, we're in a region of the galaxy rarely explored by human vessels.
[/example]

MEDIUM (3-4 lines):
[example]
[<Helm>] (not-station) (not-planet) I'm picking up some unusual energy signatures ahead.
[<Science>] Those readings don't match any known stellar phenomena.
[<Operations>] Should we investigate or maintain our current course?
[<EDCoPilot>] I recommend caution, Commander. This region is largely uncharted.
[/example]

LONGER (5-6 lines):
[example]
[<Science>] (not-station) (not-planet) The gravitational anomalies in this sector are unlike anything I've ever seen.
[<EDCoPilot>] My sensors are detecting spatial distortions that suggest ancient stellar events.
[<Crew:Tactical>] The tactical systems are registering potential threats in the vicinity.
[<Operations>] All crew stations are on high alert for any unusual activity.
[<Helm>] I'm ready to execute emergency maneuvers if needed.
[<Science>] This could be evidence of phenomena that predate human space exploration.
[/example]

Generate conversations that are:
- Focused on deep space exploration and mysteries
- Mysterious and awe-inspiring in tone
- Include appropriate speaker tags and context tags
- Engaging for space exploration enthusiasts
- Vary naturally in length (short conversations should be more common)
- Each conversation wrapped in [example]...[/example] tags
- Use the specified theme and style preferences
- Follow the content guidelines and avoid topics that should be avoided
- Ensure conversations feel natural and varied
- Mix generic and personalized content appropriately
- Incorporate recent news and events naturally when relevant

Format the output with each conversation wrapped in [example]...[/example] tags.
"""
