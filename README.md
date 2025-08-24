# EDCopilot Conversation Refresher

An automated system for generating and updating custom chatter files for the EDCopilot platform using AI language models.

## Features

- **Smart AI Conversations**: Creates fresh, engaging conversations using advanced AI (OpenAI and Claude) that sound natural and varied
- **Personal Touch**: Makes conversations feel personal by including your commander name, squadron, and preferences from your settings
- **Natural Variety**: Creates conversations that feel realistic by mixing in personal details, news references, and context tags at natural intervals
- **Fresh News & Content**: Pulls in recent Elite Dangerous Galnet to keep conversations current and relevant

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ConversationRefresher
   ```

2. **Install dependencies**
   ```bash
   py -m pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   copy env.example .env
   # Edit .env with your API keys and settings
   ```

4. **Run the updater**
   ```bash
   py src/main.py
   ```

**Note**: This project uses `py` to execute Python on Windows systems. If you're using a different operating system, replace `py` with `python` or `python3` as appropriate.

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Keys
KEY_OPENAI=your_openai_api_key_here
KEY_ANTHROPIC=your_anthropic_api_key_here

# Model Configuration
MODEL_ANTHROPIC=claude-3-7-sonnet-20250219
MODEL_OPENAI=gpt-4.1-mini

# Provider Configuration
PROVIDER_PREFERRED=OPENAI

# Directory Configuration
DIR_CUSTOM=path/to/your/edcopilot/custom/directory  # Path to EDCopilot custom files directory (used in production mode)

# Optional Configuration
LOG_LEVEL=INFO
MAX_RETRIES=3
CONTENT_LENGTH=50
CONVERSATIONS_COUNT=30  # Default number of conversation pieces to generate (when not in debug mode)
CONVERSATIONS_CHANCE_PERSONALIZATION=25  # Percentage chance for personalization references
CONVERSATIONS_CHANCE_RSS=15  # Percentage chance for RSS feed references
CONVERSATIONS_CHANCE_CONDITIONALS=10  # Percentage chance for context tags
```

### Output Routing

The system automatically routes output to the appropriate directory based on the mode:

- **Production Mode** (default): Writes directly to the EDCopilot custom directory specified in `DIR_CUSTOM`
- **Debug Mode** (`--debug`): Writes to the project's `output/` directory for testing and review

This ensures that generated content goes directly to EDCopilot when ready for use, while allowing safe testing in debug mode.

### Probability-Based Content Generation

The system uses configurable probability percentages to create natural, varied conversations:

- **Context Tags (Conditionals)**: Only 10% of conversations include context tags like `(not-station)`, `(not-planet)`, `(not-deep-space)`
- **Personalization References**: Only 25% of conversations include personal references (commander name, squadron, fleet carrier)
- **RSS Feed References**: Only 15% of conversations reference recent news and events

This ensures conversations feel natural and varied, avoiding over-personalization or excessive context tagging.

### Personalization Configuration

Create a `personalization.md` file to provide context for content generation:

```markdown
# Personalization

## Specific Data
- Commander Name: Your Commander Name
- Squadron Name: Your Squadron Name
- Theme: Your preferred themes and style

## RSS Feeds
- https://www.elitedangerous.com/en-GB/rss/galnet.xml

## Quick Notes
- Your content preferences and guidelines
- Topics to include or avoid
- Humor style and tone preferences
```

## Creating Custom Prompt Templates

The system uses template files in the `prompts/` directory to generate content. You can create and customize these templates to control the style and content of generated conversations.

**📖 For detailed template documentation, see [`prompts/README.md`](prompts/README.md)**

## Usage

### Basic Usage

Generate content for all chatter types:
```bash
py src/main.py
```

### Test Mode

Validate setup without generating content:
```bash
py src/main.py --test
```

### Debug Mode

Output generated content to the shell:
```bash
py src/main.py --debug
```

### Specific File Generation

Generate content for specific chatter types:
```bash
# Generate for one file type
py src/main.py --files chit_chat --debug

# Generate for multiple file types
py src/main.py --files space_chatter crew_chatter --debug

# Adjust the number of entries (default: 5)
py src/main.py --files deep_space_chatter --max-entries 10 --debug
```

### Personalization Control

Disable personalization features:
```bash
# Disable all personalization
py src/main.py --no-personalization

# Disable RSS feeds only
py src/main.py --no-rss

# Disable web content only
py src/main.py --no-web
```

### Content Management

Control content replacement:
```bash
# Keep existing content and merge with new content (default: replace entirely)
py src/main.py --keep-existing
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--test` | Run in test mode (validate only) |
| `--debug` | Enable debug mode - output generated content to shell |
| `--files` | Generate content for specific file types only |
| `--max-entries` | Maximum number of entries to generate per file (default: from CONVERSATIONS_COUNT config, or 5 in debug mode) |
| `--keep-existing` | Keep existing content and merge with new content (default: replace entirely) |
| `--no-personalization` | Disable personalization context |
| `--no-rss` | Disable RSS feed fetching |
| `--no-web` | Disable web content fetching |
| `--clear-cache` | Clear RSS cache before running |
| `--cache-info` | Show RSS cache information and exit |
| `--prompt-only` | enable's debug mode & outputs the prompts that would have been sent to the LLM for review placing them in the output directory |

### Available File Types

- `chit_chat` - General chit chat conversations
- `space_chatter` - Space exploration and astronomy discussions
- `crew_chatter` - Ship crew interactions and operations
- `deep_space_chatter` - Deep space exploration and mysteries

## Examples

### Generate 3 entries for chit chat with debug output:
```bash
py src/main.py --files chit_chat --debug --max-entries 3
```

### Generate content using configuration default (30 entries):
```bash
py src/main.py --files chit_chat
```

### Generate content for space and crew chatter without personalization:
```bash
py src/main.py --files space_chatter crew_chatter --no-personalization
```

### Generate 10 entries for all files with debug mode:
```bash
py src/main.py --debug --max-entries 10
```

### RSS Cache Management:
```bash
# Show cache information
py src/main.py --cache-info

# Clear cache and run
py src/main.py --clear-cache --files chit_chat
```

## Project Structure

```
ConversationRefresher/
├── src/
│   ├── config.py              # Configuration management
│   ├── main.py                # Main orchestrator
│   ├── generators/            # Content generators
│   │   ├── base_generator.py
│   │   ├── chit_chat_generator.py
│   │   ├── space_chatter_generator.py
│   │   ├── crew_chatter_generator.py
│   │   └── deep_space_chatter_generator.py
│   └── utils/                 # Utility modules
│       ├── api_client.py      # API client for OpenAI/Anthropic
│       ├── file_manager.py    # File operations and backups
│       └── personalization.py # Personalization context management
├── prompts/                   # Prompt template files
│   ├── README.md             # Template documentation
│   ├── sample.prompt.md      # Example template
│   └── prompt_*.md           # Chatter type templates
├── scheduler.py               # Windows Task Scheduler integration
├── run_updater.bat           # Simple batch script
├── run_updater.ps1           # PowerShell script
├── test_setup.py             # Setup validation
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── personalization.md        # User personalization context
├── logs/                     # Log files
├── backups/                  # Backup files
├── cache/                    # RSS cache files
└── output/                   # Generated content files
```

## Windows Integration

### Task Scheduler Setup

Use the included PowerShell script to set up automated execution:

```powershell
.\run_updater.ps1 -SetupScheduler -Frequency Weekly
```

### Manual Execution

Run the updater manually using the batch script:

```cmd
run_updater.bat
```

If you want EDCopilot to launch after the updater runs make sure you set the following in your .env file:

- START_EDCOPILOT_AFTER_UPDATE=TRUE
- DIR_EDCOPILOT=C:\Path\To\EDCopilot

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API keys are correctly set in the `.env` file
2. **Directory Not Found**: Verify the `DIR_CUSTOM` path exists and is accessible (in production mode) or check the `output/` directory (in debug mode)
3. **Permission Errors**: Run as administrator if needed for file operations
4. **Network Issues**: Check internet connectivity for API calls and RSS feeds

### Logs

Check the `logs/` directory for detailed execution logs. Log files are timestamped for easy tracking.

### Validation

Run the test script to validate your setup:

```bash
py test_setup.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Technical Constraints

### Platform Requirements
- **Operating System**: Windows 10/11 with PowerShell
- **Python Version**: Python 3.8 or higher
- **Python Execution**: Uses `py` command on Windows systems
- **API Dependencies**: OpenAI API, Anthropic Claude API access