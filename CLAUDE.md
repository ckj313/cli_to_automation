# CLI to Automation - Claude Code Context

## Project Purpose
Converts Huawei CLI commands to Python automation test scripts by calling the internal DDT CLI Parser API.

## Architecture
- `cli_to_automation.py` - Main module: API client, response parser, script generator, CLI interface
- `skill.md` - Claude Code skill definition for agent integration

## Key API
- Endpoint: `POST http://ddt.rnd.huawei.com:12240/ddt_cli_parser/testbot_query`
- Payload: `{"applicable_products": [...], "block_clis": [...]}`
- Returns JSON with `output_lines` containing automation code (e.g. `self.dta.system().sendcmd_profile(...)`)

## Development Notes
- Internal network only - API is not reachable from public internet
- The generated scripts follow the `run(dta)` function pattern for device test adapters
