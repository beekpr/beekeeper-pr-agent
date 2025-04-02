#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the project root to the Python path
# project_root = Path(__file__).parent.parent.absolute()
# sys.path.insert(0, str(project_root))

# Now import from pr_agent
from pr_agent import cli
from pr_agent.config_loader import get_settings


def main():
    # Get GitHub token from environment
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is not set")
        print("Set it with: export GITHUB_TOKEN=your_github_token")
        sys.exit(1)

    # Check for either Anthropic or OpenAI API key
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not anthropic_key and not openai_key:
        print("Error: Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY environment variable is set")
        print("Set at least one with: ")
        print("  export ANTHROPIC_API_KEY=your_anthropic_api_key")
        print("  or")
        print("  export OPENAI_API_KEY=your_openai_api_key")
        sys.exit(1)

    # Get PR URL from command line argument
    if len(sys.argv) < 2:
        print("Usage: python scripts/beekeeper_run_best_practices_check.py <PR_URL>")
        print(
            "Example: python scripts/beekeeper_run_best_practices_check.py https://github.com/beekpr/beekeeper-analytics/pull/546")
        sys.exit(1)

    pr_url = sys.argv[1]
    provider = "github"
    command = "/beekeeper_best_practices"

    # Configure settings
    get_settings().set("CONFIG.git_provider", provider)
    get_settings().set("github.user_token", github_token)

    # Configure model based on available API keys
    if anthropic_key:
        get_settings().set("anthropic.key", anthropic_key)
        get_settings().set("CONFIG.model", "anthropic/claude-3-7-sonnet-20250219")
    elif openai_key:
        get_settings().set("openai.key", openai_key)
        get_settings().set("CONFIG.model", "gpt-4-turbo")

    # Add required PR best practices settings
    get_settings().set("pr_best_practices", {
        "auto_extended_mode": False,
        "persistent_comment": True,
        "max_history_len": 4,
        "max_number_of_calls": 3,
        "parallel_calls": True
    })

    print(f"Running best practices check for {pr_url}...")
    cli.run_command(pr_url, command)


if __name__ == '__main__':
    main()