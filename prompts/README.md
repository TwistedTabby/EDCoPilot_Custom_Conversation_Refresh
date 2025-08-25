# EDCopilot Conversation Refresher - Prompt Templates

This directory contains template files for generating conversation content for different EDCopilot chatter types. These templates use variables that will be automatically replaced with actual values during content generation.

## Quick Start

Generate specific prompt files for each chatter type to get started quickly:
```bash
# Generate all prompt files
py src/main.py --generate-prompt-template

# Generate prompt files for specific chatter types only
py src/main.py --generate-prompt-template --files chit_chat crew_chatter

# Generate prompt file for one chatter type
py src/main.py --generate-prompt-template --files space_chatter

# Test your prompt file by using the "prompt-only" argument. They will appear in the output folder.
py src/main.py --files chit_chat --prompt-only
```

This will create individual prompt files for the specified chatter types (or all types if none specified) with all the available template variables and examples specific to each type.

## Usage

### Required Prompt Files

The following prompt template files must be created in the `prompts/` directory:

- `prompt_chit_chat.md` - General chit chat conversations (direct EDCopilot to commander)
- `prompt_space_chatter.md` - Space exploration and astronomy discussions
- `prompt_crew_chatter.md` - Ship crew interactions and operations
- `prompt_deep_space_chatter.md` - Deep space exploration and mysteries

### Creating Templates

1. Create a prompt template file for each chatter type (e.g., `prompt_chit_chat.md`)
2. Use the template variables above in your prompts
3. The system will automatically replace variables with actual values during generation
4. Templates support markdown formatting for better readability

## Template File Naming Convention

- `prompt_chit_chat.md` - General chit chat conversations
- `prompt_space_chatter.md` - Space exploration conversations
- `prompt_crew_chatter.md` - Crew interaction conversations
- `prompt_deep_space_chatter.md` - Deep space exploration conversations

## Example Template Structure

```markdown
# {chatter_type} Content Generation

You are generating {chatter_type} content for Elite Dangerous EDCopilot.

Generate exactly {num_entries} conversation examples that are:

- Focused on {chatter_type} themes
- Natural and engaging
- Include appropriate speaker tags
- Follow the specified format

**Personalization Guidelines:**
- Only {personalization_chance}% should include personal references
- Only {rss_chance}% should reference recent news/events
- Only {conditionals_chance}% should include context tags

**Format:**
[example]
[<Speaker>] (context-tags) Message content
[<Speaker>] Response content
[/example]

Generate content that incorporates:
- Data: {data}
- Themes: {themes}
- Conversation Styles: {conversation_styles}
- Recent news: {rss_summary}
```
## Template Variables

### Basic Variables
- `{num_entries}` - Number of conversation entries to generate
- `{chatter_type}` - The type of chatter (chit_chat, space_chatter, crew_chatter, deep_space_chatter)

### Personalization Variables
These variables are populated from the personalization.md file sections:

- `{data}` - All data from the Data section
- `{themes}` - Themes from the Themes section
- `{conversation_styles}` - Conversation styles and preferences from the Conversation Styles section
- `{rss_summary}` - Summary of recent RSS feed content from RSS Feeds section

**Note**: The personalization file should contain these sections: Data, Themes, RSS Feeds, and Conversation Styles. Other sections will be ignored.

### Configuration Variables
These variables are populated from environment configuration:

- `{personalization_chance}` - Percentage chance for personalization references (default: 25%)
- `{rss_chance}` - Percentage chance for RSS feed references (default: 15%)
- `{conditionals_chance}` - Percentage chance for context tags (default: 10%)

### Game Token Variables
These are tokens that EDCopilot will replace with actual game data:

- `<cmdrname>` - Commander's name
- `<starsystem>` - Current star system
- `<station>` - Current station name
- `<planet>` - Current planet name
- `<ship>` - Ship name
- `<credits>` - Current credits
- `<rank>` - Current rank
- `<reputation>` - Current reputation

### Speaker Tags
Different chatter types support different speaker tags:

#### Chit Chat
- No speaker tags (direct EDCopilot to commander communication)

#### Space Chatter
- `[<Helm>]` - Navigation and piloting observations
- `[<EDCoPilot>]` - AI assistant responses about space
- `[<Science>]` - Scientific observations and analysis
- `[<Operations>]` - General space observations
- `[<Tactical>]` - Space hazards and navigation warnings
- `[<Communications>]` - Communications about space phenomena

#### Crew Chatter
- `[<Number1>]` - First crew member
- `[<Science>]` - Scientific observations and analysis
- `[<Helm>]` - Navigation and piloting
- `[<Operations>]` - General operations and status
- `[<Engineering>]` - Ship systems and maintenance
- `[<Comms>]` - Communications and external contact
- `[<EDCoPilot>]` - The ship's computer (AI assistant responses)
- `[<Crew:Medical>]` - Medical crew member
- `[<Crew:Tactical>]` - Tactical crew member
- `[<Crew:Maintenance>]` - Maintenance crew member
- `[<Crew:Security>]` - Security crew member

#### Deep Space Chatter
All crew chatter speakers plus:
- `[<Ship1>]` - First ship encounter
- `[<Ship2>]` - Second ship encounter
- `[<Ship3>]` - Third ship encounter
- `[<Ship4>]` - Fourth ship encounter

### Context Tags
Optional context tags that can be used on the first line of conversations:

- `(not-station)` - Will not pick this conversation if currently at/around a station
- `(not-planet)` - Will not pick this conversation if currently on or approaching a planet
- `(not-deep-space)` - Will not pick this conversation if currently in deep space (> 5000 ly from Sol and Colonia)

### Conversation Length Distribution
The system automatically varies conversation lengths with this distribution:
- 40% short conversations (1-2 lines of dialogue)
- 35% medium conversations (3-4 lines of dialogue)
- 20% longer conversations (5-6 lines of dialogue)
- 5% extended conversations (7+ lines of dialogue)

### Format Examples

#### Chit Chat Format
```
Hello <cmdrname>, how can I assist you today?
We are currently in the <starsystem> system.
Your <ship> is looking good, Commander.
```

#### Conversation Format (Space/Crew/Deep Space)
```
[example]
[<Speaker>] (context-tags) Message content
[<Speaker>] Response content
[/example]
```
