#!/usr/bin/env python3
"""
CLI to Automation Script Generator

Calls the DDT CLI Parser API to convert Huawei CLI commands
into executable automation test scripts.

Usage:
    python cli_to_automation.py --product USG6000F --cli "display ospf peer" "system-view" "ospf 1"
    python cli_to_automation.py --product USG6000F --cli-file commands.txt
    python cli_to_automation.py --product USG6000F --cli "display ospf peer" --output script.py
"""

import argparse
import json
import sys
from pathlib import Path

import requests

DDT_API_URL = "http://ddt.rnd.huawei.com:12240/ddt_cli_parser/testbot_query"
DEFAULT_TIMEOUT = 60


def call_ddt_api(cli_commands: list[str], products: list[str], timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Call the DDT CLI Parser API to parse CLI commands.

    Args:
        cli_commands: List of CLI command strings to parse.
        products: List of applicable product models (e.g. ['USG6000F']).
        timeout: Request timeout in seconds.

    Returns:
        API response as a dictionary.

    Raises:
        requests.RequestException: If the API call fails.
        ValueError: If the API returns an error status.
    """
    # Join all CLI commands into a single string separated by \n
    cli_block = "\n".join(cli_commands)
    payload = {
        "applicable_products": products,
        "block_clis": [cli_block],
    }

    response = requests.post(
        DDT_API_URL,
        json=payload,
        timeout=timeout,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    response.raise_for_status()

    data = response.json()
    if data.get("status") != "SUCCESS":
        raise ValueError(f"API error: {data.get('message', 'Unknown error')}")

    return data


def extract_automation_lines(api_response: dict) -> list[str]:
    """Extract automation code lines from the API response.

    Args:
        api_response: The parsed JSON response from the DDT API.

    Returns:
        List of automation code lines.
    """
    lines = []
    result = api_response.get("result", {})

    for _key, entry in sorted(result.items()):
        if entry.get("status") != "SUCCESS":
            error_msg = entry.get("error_message", "Unknown error")
            lines.append(f"# ERROR: {error_msg}")
            continue

        output = entry.get("output_lines", "")
        if output:
            for line in output.strip().splitlines():
                stripped = line.strip()
                if stripped:
                    lines.append(stripped)

    return lines


def generate_script(automation_lines: list[str], products: list[str], cli_commands: list[str]) -> str:
    """Generate automation script output from the API response.

    Directly outputs the automation lines returned by the API,
    without wrapping in a function definition.

    Args:
        automation_lines: Extracted automation code lines from the API.
        products: Product models used in the request.
        cli_commands: Original CLI commands for reference.

    Returns:
        Automation code lines as a string.
    """
    if not automation_lines:
        return "# No automation lines generated\n"

    return "\n".join(automation_lines) + "\n"


def read_cli_from_file(filepath: str) -> list[str]:
    """Read CLI commands from a text file, one command per line.

    Args:
        filepath: Path to the text file.

    Returns:
        List of CLI command strings.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CLI file not found: {filepath}")

    commands = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            commands.append(stripped)

    return commands


def main():
    parser = argparse.ArgumentParser(
        description="Convert Huawei CLI commands to automation test scripts via DDT API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --product USG6000F --cli "display ospf peer"
  %(prog)s --product USG6000F --cli "system-view" "ospf 1" "display this"
  %(prog)s --product USG6000F --cli-file commands.txt --output test_script.py
  %(prog)s --product USG6000F USG6000E --cli "display interface brief"
        """,
    )

    parser.add_argument(
        "--product",
        nargs="+",
        required=True,
        help="Device product model(s), e.g. USG6000F",
    )

    cli_group = parser.add_mutually_exclusive_group(required=True)
    cli_group.add_argument(
        "--cli",
        nargs="+",
        help="CLI command(s) to convert",
    )
    cli_group.add_argument(
        "--cli-file",
        help="Path to a text file with CLI commands (one per line)",
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file path for the generated script (default: stdout)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"API request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output raw API JSON response instead of a script",
    )

    parser.add_argument(
        "--api-url",
        default=DDT_API_URL,
        help=f"DDT API endpoint URL (default: {DDT_API_URL})",
    )

    args = parser.parse_args()

    # Gather CLI commands
    if args.cli_file:
        cli_commands = read_cli_from_file(args.cli_file)
    else:
        cli_commands = args.cli

    if not cli_commands:
        parser.error("No CLI commands provided.")

    # Call the API
    try:
        api_response = call_ddt_api(
            cli_commands=cli_commands,
            products=args.product,
            timeout=args.timeout,
        )
    except requests.ConnectionError:
        print("Error: Cannot connect to DDT API. Are you on the internal network?", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: API request timed out after {args.timeout}s.", file=sys.stderr)
        sys.exit(1)
    except (requests.RequestException, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.output_json:
        output = json.dumps(api_response, indent=2, ensure_ascii=False)
    else:
        automation_lines = extract_automation_lines(api_response)
        output = generate_script(automation_lines, args.product, cli_commands)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Script written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
