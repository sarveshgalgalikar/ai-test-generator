"""
AI Test Case Generator v1.0
Generates structured QA test cases using Claude API.
"""

import anthropic
import json
import argparse
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# --- Configuration ---
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
PROMPT_VERSION = "v1"
PROMPT_PATH = Path("prompts/system_v1.txt")
OUTPUT_DIR = Path("output")
LOG_DIR = Path("logs")


def load_prompt():
    """Load system prompt from versioned file."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_PATH}")
    return PROMPT_PATH.read_text().strip()


def call_claude(system_prompt, user_message):
    """Make API call to Claude with logging and error handling."""
    client = anthropic.Anthropic()

    start_time = time.time()

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        latency = time.time() - start_time

        # Extract usage stats
        usage = {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
            "latency_seconds": round(latency, 2),
            "estimated_cost_usd": round(
                (message.usage.input_tokens * 3 / 1_000_000) +
                (message.usage.output_tokens * 15 / 1_000_000), 6
            )
        }

        return message.content[0].text, usage

    except anthropic.AuthenticationError:
        print("ERROR: Invalid API key. Check your .env file.")
        return None, None
    except anthropic.RateLimitError:
        print("ERROR: Rate limited. Wait a moment and try again.")
        return None, None
    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        return None, None


def parse_response(response_text):
    """Parse JSON from Claude's response, handling markdown fences."""
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        cleaned = cleaned.rsplit("```", 1)[0]

    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        print(f"Raw response:\n{response_text[:500]}")
        return None


def save_json(test_data, feature_name):
    """Save test cases as JSON file."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = feature_name.lower().replace(" ", "_")[:30]
    filepath = OUTPUT_DIR / f"{safe_name}_{timestamp}.json"

    with open(filepath, "w") as f:
        json.dump(test_data, f, indent=2)

    return filepath


def save_markdown(test_data, feature_name):
    """Save test cases as readable Markdown file."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = feature_name.lower().replace(" ", "_")[:30]
    filepath = OUTPUT_DIR / f"{safe_name}_{timestamp}.md"

    lines = [
        f"# Test Cases: {test_data['feature']}",
        f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_",
        f"_Prompt Version: {PROMPT_VERSION} | Model: {MODEL}_\n",
        f"**Total Cases: {test_data.get('total_cases', len(test_data['test_cases']))}**\n",
        "---\n"
    ]

    for tc in test_data["test_cases"]:
        lines.append(f"## TC-{tc['id']}: {tc['title']}\n")
        lines.append(f"- **Type:** {tc['type']}")
        lines.append(f"- **Priority:** {tc['priority']}")
        lines.append(f"- **Preconditions:** {tc.get('preconditions', 'N/A')}")
        lines.append(f"- **Test Data:** {tc.get('test_data', 'N/A')}\n")
        lines.append("**Steps:**\n")
        for i, step in enumerate(tc["steps"], 1):
            lines.append(f"{i}. {step}")
        lines.append(f"\n**Expected Result:** {tc['expected_result']}\n")
        lines.append("---\n")

    filepath.write_text("\n".join(lines))
    return filepath


def save_log(feature, usage, prompt_version):
    """Log API call details for observability."""
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / "api_calls.jsonl"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "feature": feature,
        "model": MODEL,
        "prompt_version": prompt_version,
        **usage
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def display_test_cases(test_data):
    """Pretty-print test cases to terminal."""
    print(f"\n{'='*60}")
    print(f"TEST CASES FOR: {test_data['feature']}")
    print(f"{'='*60}")

    for tc in test_data["test_cases"]:
        print(f"\n--- TC-{tc['id']}: {tc['title']} ---")
        print(f"  Type:          {tc['type']}")
        print(f"  Priority:      {tc['priority']}")
        print(f"  Preconditions: {tc.get('preconditions', 'N/A')}")
        print(f"  Test Data:     {tc.get('test_data', 'N/A')}")
        print(f"  Steps:")
        for i, step in enumerate(tc["steps"], 1):
            print(f"    {i}. {step}")
        print(f"  Expected:      {tc['expected_result']}")

    print(f"\n{'='*60}")
    print(f"Total: {len(test_data['test_cases'])} test cases generated")


def main():
    parser = argparse.ArgumentParser(description="AI Test Case Generator")
    parser.add_argument("--feature", "-f", type=str, help="Feature description")
    parser.add_argument("--count", "-c", type=int, default=5, help="Number of test cases")
    parser.add_argument("--output", "-o", choices=["json", "markdown", "both"], default="both",
                        help="Output format")
    args = parser.parse_args()

    # Get feature from arg or prompt
    feature = args.feature or input("Describe the feature to test: ")

    if not feature.strip():
        print("ERROR: Feature description cannot be empty.")
        return

    print(f"\nGenerating {args.count} test cases...")
    print(f"Model: {MODEL} | Prompt: {PROMPT_VERSION}\n")

    # Load prompt and call API
    system_prompt = load_prompt()
    user_message = f"Generate {args.count} test cases for this feature: {feature}"
    response_text, usage = call_claude(system_prompt, user_message)

    if not response_text:
        return

    # Parse response
    test_data = parse_response(response_text)
    if not test_data:
        return

    # Display results
    display_test_cases(test_data)

    # Save outputs
    if args.output in ("json", "both"):
        json_path = save_json(test_data, feature)
        print(f"\nSaved JSON:     {json_path}")

    if args.output in ("markdown", "both"):
        md_path = save_markdown(test_data, feature)
        print(f"Saved Markdown: {md_path}")

    # Log the API call
    save_log(feature, usage, PROMPT_VERSION)
    print(f"\nAPI Usage: {usage['input_tokens']} in / {usage['output_tokens']} out "
          f"| Latency: {usage['latency_seconds']}s "
          f"| Cost: ${usage['estimated_cost_usd']:.4f}")


if __name__ == "__main__":
    main()