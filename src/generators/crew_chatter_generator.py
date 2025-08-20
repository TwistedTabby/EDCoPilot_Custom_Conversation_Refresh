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
This content will be used for conversations between ship crew members and about ship operations.

Generate exactly {num_entries} crew-related conversation examples that follow the EDCopilot format:

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

Note: For specialized crew roles, use the format [<Crew:Role>] where Role is the specific job (e.g., [<Crew:Medical>], [<Crew:Tactical>], [<Crew:Maintenance>], etc.)

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
[<Helm>] (not-station) (not-planet) Computer, plot a course to the nearest station.
[<EDCoPilot>] Course plotted, Commander.
[/example]

MEDIUM (3-4 lines):
[example]
[<Engineering>] (not-station) (not-planet) Captain, we're running low on fuel.
[<Operations>] How much do we have left?
[<Engineering>] About 15% remaining.
[<Helm>] I'll find us a fuel depot immediately.
[/example]

LONGER (5-6 lines):
[example]
[<Crew:Tactical>] (not-station) Multiple hostiles detected on our six!
[<Helm>] Evasive maneuvers initiated.
[<Engineering>] Shields are holding at 85%.
[<Operations>] Weapons systems are fully charged.
[<Crew:Tactical>] Target acquired, ready to engage.
[<Helm>] Engaging now!
[/example]

Generate conversations that are:
- Focused on ship operations and crew interactions
- Professional but friendly in tone
- Include appropriate speaker tags and context tags
- Realistic for a space ship crew
- Vary naturally in length (short conversations should be more common)
- Each conversation wrapped in [example]...[/example] tags

Format the output with each conversation wrapped in [example]...[/example] tags.
"""
