# Sample Prompt Template

This is a sample prompt template that demonstrates how to use template variables and create custom conversation content for EDCopilot.

## Template Purpose

This template shows the structure and variables you can use when creating custom prompt files for different chatter types.

## Basic Template Structure

You are generating {chatter_type} content for Elite Dangerous EDCopilot. 
This content will be used for conversations about {chatter_type} topics.

Generate exactly {num_entries} conversation examples that follow the EDCopilot format:

## Personalization Context

**Data:**
{data}

**Themes:**
{themes}

**Conversation Styles:**
{conversation_styles}

## Recent Context and News

{rss_summary}

## Conversation Length Distribution

IMPORTANT: Vary the conversation lengths naturally. Aim for this distribution:
- 40% short conversations (1-2 lines of dialogue)
- 35% medium conversations (3-4 lines of dialogue) 
- 20% longer conversations (5-6 lines of dialogue)
- 5% extended conversations (7+ lines of dialogue)

## Format

Each conversation should be wrapped in [example]...[/example] tags.

Format: 
```
[example]
[<Speaker>] (context-tags) Message content
[<Speaker>] (context-tags) Response content
[/example]
```

## Available Speakers

Choose appropriate speakers for your chatter type:

### For Space Chatter:
- `[<Helm>]` - Navigation and piloting observations
- `[<EDCoPilot>]` - AI assistant responses about space
- `[<Science>]` - Scientific observations and analysis
- `[<Operations>]` - General space observations
- `[<Tactical>]` - Space hazards and navigation warnings
- `[<Communications>]` - Communications about space phenomena

### For Crew Chatter:
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

### For Deep Space Chatter:
All crew chatter speakers plus:
- `[<Ship1>]` - First ship encounter
- `[<Ship2>]` - Second ship encounter
- `[<Ship3>]` - Third ship encounter
- `[<Ship4>]` - Fourth ship encounter

## Context Tags

Context tags to use (OPTIONAL - only on the first line of each conversation):
- `(not-station)` - Will not pick this conversation if you are currently at/around a station
- `(not-planet)` - Will not pick this conversation if you are currently on or approaching a planet
- `(not-deep-space)` - Will not pick this conversation if you are currently out in deep space (> 5000 ly from Sol and Colonia)

IMPORTANT: Context tags are optional and should only be used on the first line of each conversation when relevant.

## Probability Guidelines

- Only {conditionals_chance}% of conversations should include context tags
- Only {personalization_chance}% of conversations should include personal references
- Only {rss_chance}% of conversations should reference recent news/events
- Most conversations ({100-conditionals_chance}%) should NOT have context tags
- When context tags are used, they should only appear on the first line

## Game Token Variables

You can include these tokens that EDCopilot will replace with actual game data:
- `<cmdrname>` - Commander's name
- `<starsystem>` - Current star system
- `<station>` - Current station name
- `<planet>` - Current planet name
- `<ship>` - Ship name
- `<credits>` - Current credits
- `<rank>` - Current rank
- `<reputation>` - Current reputation

## Examples of Different Conversation Lengths

### SHORT (1-2 lines):
```
[example]
[<Science>] (not-station) (not-planet) That's a beautiful binary star system.
[<EDCoPilot>] Indeed, Commander. The gravitational dance between those stars is fascinating.
[/example]
```

### MEDIUM (3-4 lines):
```
[example]
[<Helm>] (not-station) The colors in this nebula are absolutely breathtaking!
[<Science>] Those colors indicate different elements being ionized by nearby stars.
[<Operations>] We're detecting unusual radiation patterns from that distant star cluster.
[<EDCoPilot>] The radiation suggests recent supernova activity in that region.
[/example]
```

### LONGER (5-6 lines):
```
[example]
[<Science>] (not-station) (not-planet) Did you know that Betelgeuse is expected to go supernova within the next 100,000 years?
[<EDCoPilot>] That's correct, Commander. Betelgeuse is a red supergiant star in the constellation Orion.
[<Operations>] When it does go supernova, it will be visible even during the day.
[<Science>] The explosion will release elements like carbon, oxygen, and iron into space.
[<Helm>] It's amazing how the death of one star creates the building blocks for new ones.
[<EDCoPilot>] The cycle of stellar birth and death is fundamental to cosmic evolution.
[/example]
```

## Content Guidelines

Generate conversations that are:
- Focused on {chatter_type} themes
- Educational and informative
- Include appropriate speaker tags and context tags
- Engaging for space enthusiasts
- Vary naturally in length (short conversations should be more common)
- Each conversation wrapped in [example]...[/example] tags
- Use the specified theme and style preferences
- Follow the content guidelines and avoid topics that should be avoided
- Ensure conversations feel natural and varied
- Mix generic and personalized content appropriately
- Incorporate recent news and events naturally when relevant

## Customization Tips

1. **Replace {chatter_type}** with your specific chatter type (space_chatter, crew_chatter, deep_space_chatter)
2. **Adjust speaker lists** to match your chatter type requirements
3. **Modify content guidelines** to focus on your specific themes
4. **Add custom examples** that demonstrate your desired conversation style
5. **Include specific topics** relevant to your chatter type

Format the output with each conversation wrapped in [example]...[/example] tags.
