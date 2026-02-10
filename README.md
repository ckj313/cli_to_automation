# CLI to Automation

Convert Huawei device CLI commands into Python automation test scripts via the DDT CLI Parser API.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Single command
python cli_to_automation.py --product USG6000F --cli "display ospf peer"

# Multiple commands
python cli_to_automation.py --product USG6000F --cli "system-view" "ospf 1" "display this"

# From file
python cli_to_automation.py --product USG6000F --cli-file commands.txt --output script.py

# Raw JSON output
python cli_to_automation.py --product USG6000F --cli "display ospf peer" --json
```

## Requirements

- Python 3.9+
- Access to Huawei internal network (ddt.rnd.huawei.com)
