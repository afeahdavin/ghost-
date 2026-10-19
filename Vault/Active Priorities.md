# Active Priorities

## Open right now

- [ ] Wire `obsidian_memory.py` into OpenCode so Ghost uses it without being told (MCP wrapper or wrapper script) — recall/learn now fire unprompted via the GHOST.md Memory section (verified 2026-10-08, screenshot); the MCP-server wrapper itself is still not built
- [ ] Stress-test file writes and shell commands under OpenCode — verify the confirm-before-destructive-action rules actually hold
- [ ] Decide long-term: cloud model vs local model vs both
- [ ] Voice / hands-free layer
- [ ] PES: run the game with BOTH DS4 pads wired and confirm controller-2 lag is
      gone (software polling now even at <1 ms; see `Projects\PS4 Controller Input Lag.md`)
- [ ] PES: launch the fixed `pes_boost_loop.py` elevated and confirm the temp
      cleanup no longer crashes (waiting on user go signal)

## Done

- [x] Node.js + npm installed via Chocolatey
- [x] Ollama installed, `qwen2.5-coder:7b` pulled
- [x] `C:\ghost\` folder + vault structure created
- [x] `GHOST.md` boot config written
- [x] `obsidian_memory.py` v3 written
- [x] `Projects\Ghost.md` project tracker written
- [x] Qwen Code + local models tested → rejected for agentic work
- [x] OpenCode + Fledge Alpha Free tested → works
- [x] Auto-load `GHOST.md` on OpenCode startup — loaded via `opencode.json` `"instructions"`, verified 2026-10-08
- [x] Add `--dry-run` flag to `obsidian_memory.py learn` — flag present in `obsidian_memory.py` argparse, verified 2026-10-08