# AI Test Case Generator

An AI-powered CLI tool that generates structured, production-quality QA test cases using Claude API.

## Features

- Generates test cases with edge cases, security, boundary, i18n, and accessibility coverage
- Structured JSON output for automation pipelines
- Markdown output for human review
- Token usage tracking and cost estimation
- Versioned prompt engineering
- Full API call logging

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your-key-here
```

## Usage
```bash
# Interactive mode
python3 test_generator.py

# CLI mode
python3 test_generator.py --feature "Login form with OAuth" --count 5

# JSON only
python3 test_generator.py -f "Shopping cart" -c 3 -o json
```

## Architecture

- **Prompt versioning** — System prompts stored in `prompts/` for iteration tracking
- **Structured output** — Claude returns JSON parsed and validated by the tool
- **Observability** — Every API call logged with tokens, latency, and cost
- **Security** — API keys in `.env`, excluded via `.gitignore`

## Tech Stack

- Python 3.12
- Anthropic Claude API (Sonnet)
- python-dotenv

## Author

Built as part of an AI Engineering learning path.