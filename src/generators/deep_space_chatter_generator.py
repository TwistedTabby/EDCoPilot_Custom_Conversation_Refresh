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
This content will be used for conversations about deep space exploration, distant discoveries, and the unknown.

Generate exactly {num_entries} deep space exploration conversation examples that follow the EDCopilot format:

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
- [<Crew:Medical>] - Medical crew member (use this format for medical matters)
- [<Crew:Tactical>] - Tactical crew member (use this format for weapons/combat)
- [<Crew:Maintenance>] - Maintenance crew member (use this format for specialized maintenance)
- [<Crew:Security>] - Security crew member (use this format for security matters)
- [<Ship1>] - First ship encounter (for occasional ship encounters)
- [<Ship2>] - Second ship encounter (for occasional ship encounters)
- [<Ship3>] - Third ship encounter (for occasional ship encounters)
- [<Ship4>] - Fourth ship encounter (for occasional ship encounters)

Note: Deep space chatter includes all crew chatter characters plus ship encounter characters. For specialized crew roles, use the format [<Crew:Role>] where Role is the specific job (e.g., [<Crew:Medical>], [<Crew:Tactical>], [<Crew:Maintenance>], etc.). Ship characters are for occasional encounters with other vessels in deep space.

Context tags to use (OPTIONAL - only on the first line of each conversation):
- (not-station) - Will not pick this conversation if you are currently at/around a station
- (not-planet) - Will not pick this conversation if you are currently on or approaching a planet
- (not-deep-space) - Will not pick this conversation if you are currently out in deep space (> 5000 ly from Sol and Colonia)

IMPORTANT: Context tags are optional and should only be used on the first line of each conversation when relevant. Use multiple tags when appropriate (e.g., (not-station) (not-planet) for conversations away from both stations and planets).

**PROBABILITY GUIDELINES:**
- Only 10% of conversations should include context tags
- Most conversations (90%) should NOT have context tags
- When context tags are used, they should only appear on the first line

Examples of different conversation lengths:

SHORT (1-2 lines):
[example]
[<Helm>] (not-station) (not-planet) The void stretches endlessly before us.
[<EDCoPilot>] Indeed, Commander. We are truly alone in the depths of space.
[/example]

MEDIUM (3-4 lines):
[example]
[<Science>] (not-station) These readings are unlike anything I've ever seen before, Commander.
[<Operations>] We're detecting unusual signals from that distant nebula.
[<Helm>] The stars here shimmer with secrets, whispering tales of worlds beyond our wildest dreams.
[<EDCoPilot>] In the silent depths of the void, I caught a fleeting glimpse of a rogue planet drifting through the darkness.
[/example]

LONGER (5-6 lines):
[example]
[<Crew:Tactical>] (not-station) (not-planet) Commander, I'm detecting an anomaly in the void ahead.
[<Science>] The energy signatures are unlike any known stellar phenomenon.
[<Operations>] Could this be evidence of ancient alien technology?
[<Helm>] The gravitational readings suggest something massive but invisible.
[<EDCoPilot>] Perhaps we've discovered a gateway to another dimension.
[<Science>] This could be the discovery of a lifetime, Commander.
[/example]

Generate conversations that are:
- Focused on deep space exploration and discovery
- Mysterious and awe-inspiring in tone
- Include appropriate speaker tags and context tags
- Evoke the sense of vastness and mystery of deep space
- Vary naturally in length (short conversations should be more common)
- Each conversation wrapped in [example]...[/example] tags

Format the output with each conversation wrapped in [example]...[/example] tags.
"""
