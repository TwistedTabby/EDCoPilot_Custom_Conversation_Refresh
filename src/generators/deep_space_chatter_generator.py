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
While onboard our ship, we may hear our crew talking among themselves . They may be discussing ship operations, making small talk, or talking about places of interest in our vicinity.
This content will be used when you are more than 5000 light-years from both Sol and Colonia. You can use this type of chatter to focus conversations more on exploration, crew morale, ship maintenance, unexplained phenomena.

Generate exactly {num_entries} deep space exploration conversation examples that follow the EDCopilot format:

## Personalization Context

**Facts:**
{{data}}

IMPORTANT: Vary the conversation lengths naturally. Aim for this distribution:
- 40% short conversations (1-2 lines of dialogue)
- 35% medium conversations (3-4 lines of dialogue) 
- 20% longer conversations (5-6 lines of dialogue)
- 5% extended conversations (7+ lines of dialogue)

Each conversation should be wrapped in [example]...[/example] tags.

Available speakers:
- [<Number1>] - First crew member
- [<Science>] - Scientific observations and analysis
- [<Helm>] - Navigation and piloting
- [<Operations>] - General operations and status
- [<Engineering>] - Ship systems and maintenance
- [<Comms>] - Communications and external contact
- [<EDCoPilot>] - The ship's computer (AI assistant responses)
- [<Crew:ROLE>] - If used, create a role name to replace ROLE
- [<Ship1>] - First ship encounter
- [<Ship2>] - Second ship encounter
- [<Ship3>] - Third ship encounter
- [<Ship4>] - Fourth ship encounter

Condition tags to use (OPTIONAL - only on the first line of each conversation and can include multiple conditions):
- (not-station) - Will not pick this conversation if you are currently at/around a station
- (not-planet) - Will not pick this conversation if you are currently on or approaching a planet
- (not-deep-space) - Will not pick this conversation if you are currently out in deep space (> 5000 ly from Sol and Colonia)

Tokens that can be used in the conversation:
- <cmdrname> : your Commander's name (without the “Commander” at the beginning)
- <cmdraddress> : will be replaced by Sir, Ma'am, or Commander based on the gender you have set in Settings
- <myshipname> : the name of your active ship
- <fuellevels> : will be replaced by your current fuel level percentage number
- <starsystem> : name of your current system
- <randomstarsystem> : name of a random populated system
- <stationname> : name of the current station you are at
- <fcCaptain> : name of your Fleet Carrier Captain

**PROBABILITY GUIDELINES:**
- Only {{conditionals_chance}}% of conversations should include context tags
- Most conversations ({{100-conditionals_chance}}%) should NOT have context tags
- When context tags are used, they should only appear on the first line
- Only {{personalization_chance}}% of conversations should include personal references
- Only {{rss_chance}}% of conversations should reference recent news/events

Examples of different conversation lengths:

SHORT (1-2 lines):
[example]
[<Science>] The stellar density out here is absolutely incredible.
[<EDCoPilot>] Indeed, we're in a region of the galaxy rarely explored by human vessels.
[/example]

MEDIUM (3-4 lines):
[example]
[<Helm>] (not-station) I'm picking up some unusual energy signatures ahead.
[<Science>] Those readings don't match any known stellar phenomena.
[<Operations>] Should we investigate or maintain our current course?
[<EDCoPilot>] I recommend caution, Commander. This region is largely uncharted.
[/example]

LONGER (5-6 lines):
[example]
[<Science>] (not-station) The gravitational anomalies in this sector are unlike anything I've ever seen.
[<EDCoPilot>] My sensors are detecting spatial distortions that suggest ancient stellar events.
[<Crew:Tactical>] The tactical systems are registering potential threats in the vicinity.
[<Operations>] All crew stations are on high alert for any unusual activity.
[<Helm>] I'm ready to execute emergency maneuvers if needed.
[<Science>] This could be evidence of phenomena that predate human space exploration.
[/example]

Generate conversations that are:
- Focused on deep space exploration and mysteries
- Focused on ship crew interactions and operations
- Mysterious and awe-inspiring in tone
- Engaging for space exploration enthusiasts
- Ensure conversations feel natural and varied
- Mix generic and personalized content appropriately
- Include appropriate speaker tags and condition tags
- Engaging for space simulation enthusiasts
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
