# CLI to Automation Script Generator

Convert Huawei device CLI commands into executable Python automation test scripts using the DDT CLI Parser API.

## When to use this skill

Use this skill when the user wants to:
- Convert CLI commands (e.g. `display ospf peer`, `system-view`, `ospf 1`) into automation test scripts
- Generate Python automation scripts for Huawei device testing
- Parse CLI commands through the DDT API for a specific device model (e.g. USG6000F)
- Batch-convert multiple CLI commands into a single automation script

## Workflow

1. **Collect inputs** from the user:
   - **CLI commands**: One or more Huawei CLI commands to convert
   - **Device product model**: The applicable device type (e.g. `USG6000F`, `USG6000E`)
   - **Output preference**: Script file path or display in terminal

2. **Call the DDT API** using the `cli_to_automation.py` tool:

```bash
# Single command
python /Users/ccc/Documents/code/cli_to_automation/cli_to_automation.py \
  --product USG6000F \
  --cli "display ospf peer"

# Multiple commands
python /Users/ccc/Documents/code/cli_to_automation/cli_to_automation.py \
  --product USG6000F \
  --cli "system-view" "ospf 1" "area 0" "network 10.0.0.0 0.0.0.255" "quit" "quit" "display ospf peer"

# From a file (one command per line)
python /Users/ccc/Documents/code/cli_to_automation/cli_to_automation.py \
  --product USG6000F \
  --cli-file commands.txt

# Save to file
python /Users/ccc/Documents/code/cli_to_automation/cli_to_automation.py \
  --product USG6000F \
  --cli "display ospf peer" \
  --output test_ospf.py

# Get raw JSON response
python /Users/ccc/Documents/code/cli_to_automation/cli_to_automation.py \
  --product USG6000F \
  --cli "display ospf peer" \
  --json
```

3. **Review the output**: The generated script contains a `run(dta)` function with the converted automation lines.

## API Details

- **Endpoint**: `http://ddt.rnd.huawei.com:12240/ddt_cli_parser/testbot_query`
- **Method**: POST
- **Payload**: `{"applicable_products": ["USG6000F"], "block_clis": ["display ospf peer", ...]}`
- **Response**: JSON with `status`, `message`, and `result` containing `output_lines` per command block

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--product` | Yes | Device model(s), e.g. `USG6000F` |
| `--cli` | Yes* | CLI command(s) to convert |
| `--cli-file` | Yes* | Text file with CLI commands (one per line) |
| `--output` / `-o` | No | Output file path (default: stdout) |
| `--json` | No | Output raw API JSON instead of script |
| `--timeout` | No | API timeout in seconds (default: 60) |
| `--api-url` | No | Override the DDT API URL |

*One of `--cli` or `--cli-file` is required.

## Example interaction

**User**: Help me convert these CLI commands to an automation script for USG6000F:
```
system-view
ospf 1
area 0
network 10.0.0.0 0.0.0.255
quit
quit
display ospf peer
```

**Agent**: Runs the tool and presents the generated Python script with `run(dta)` function containing the automation commands.

## Error handling

- If the API is unreachable, remind the user they must be on the internal network
- If a specific CLI command fails parsing, the script will include a comment indicating the error
- The `--json` flag can be used for debugging API responses

## Important notes

- This tool requires access to the Huawei internal network (ddt.rnd.huawei.com)
- The `requests` Python library must be installed (`pip install requests`)
- Commands are sent as a block to the API, preserving their order
