# Project: Jarvis

The local agent system itself — this document tracks its own build.

## Current stack (as of Oct 2026 testing)

- **Hands:** OpenCode (`opencode-ai`), running in `E:\jarvis`.
- **Brain:** Fledge Alpha Free, via OpenCode Zen (cloud, not local).
- **Boot config:** `E:\jarvis\QWEN.md` — identity, rules. Written for
  Qwen Code originally; still read and followed correctly under OpenCode,
  but the model/tool lines inside it are stale (see Known issues).
- **Memory:** this vault, at `E:\jarvis\Vault`.
- **Retrieval:** `E:\jarvis\obsidian_memory.py` — TF-IDF search over
  `Memory/`, via `remember` / `recall` commands. Not yet wired into
  OpenCode automatically — still manual.

## Hands: tested and working (OpenCode + Fledge Alpha Free)

- [x] Real tool calls — `read_file`, `Glob`, web search — all confirmed
      correctly formed and executed.
- [x] Folder listing (`Glob "*"`) — correct results, ~6s.
- [x] File read + summarize (`@VAULT-INDEX.md summarize`) — correct,
      accurate summary, ~7s. This is the exact test that failed under
      both local models below.
- [x] Live web search — correctly answered a current-events question
      (Portugal national team manager) by searching rather than
      guessing, confirmed against real sources.
- [ ] Not yet tested: file writes/edits, running shell commands,
      multi-step chained tasks, confirmation-gating on destructive
      actions (the rules in `QWEN.md` governing this have not been
      stress-tested under OpenCode).

## Hands: tested and rejected (Qwen Code + local Ollama)

- [x] `qwen2.5-coder:7b` via Qwen Code — tool calls not formed at all;
      model printed fake JSON as plain text instead of calling tools.
      Confirmed broken even when explicitly told "do not call tools."
- [x] `qwen3:8b` via Qwen Code — attempted real tool calls but
      consistently malformed them (missing required `name` field).
      Confirmed broken across 4+ separate attempts, different commands.
- **Conclusion:** not a config or prompt problem — Qwen Code's
      tool-call bridge does not reliably work with either model tested
      on Ollama. Shelved for agentic work. Either model still works
      fine for plain chat/code help outside the agent loop (confirmed
      via `ollama run` directly).

## Known issues

- `QWEN.md` still states the model is `qwen2.5-coder:7b` via Ollama —
  stale, needs updating to reflect the actual current stack above.
- Not fully local anymore. Fledge Alpha Free runs on OpenCode's
  servers, not this machine. Accepted tradeoff for now, since it's the
  first setup that actually works end to end — revisit if privacy/
  offline-only becomes a hard requirement.
- `obsidian_memory.py` is not yet connected automatically — Jarvis has
  to be told to call `remember`/`recall` each session rather than doing
  it on its own initiative.

## Not built yet

- [ ] Voice / hands-free layer (wake word, mic input, text-to-speech) —
      the "Tony Stark talking to the room" piece. Not started.
- [ ] Automatic memory wiring (MCP-server wrapper or equivalent) so
      `remember`/`recall` fire without being asked each session.
- [ ] File-write and shell-command testing under OpenCode — confirm the
      confirm-before-destructive-action rules actually hold up once
      Jarvis can modify things, not just read them.
- [ ] Update `QWEN.md` to match the current stack (see Known issues).
