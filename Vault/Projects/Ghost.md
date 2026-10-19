# Project: Ghost

The local agent system itself — this document tracks its own build.

## Current stack (as of Oct 2026 testing)

- **Hands:** OpenCode (`opencode-ai`), running in `C:\ghost`.
- **Brain:** Fledge Alpha Free, via OpenCode Zen (cloud, not local).
- **Boot config:** `C:\ghost\GHOST.md` — identity, rules. Auto-loads via
  `opencode.json` (`"instructions": ["GHOST.md"]`); startup sequence
  auto-executes on a fresh session.
- **Memory:** this vault, at `C:\ghost\Vault`.
- **Human interface:** Obsidian, pointed at `C:\ghost\Vault`.
- **Retrieval:** `C:\ghost\obsidian_memory.py` — v3.1, Ollama embeddings
  (`nomic-embed-text`) with a cached vector store and an LLM-driven
  `learn()` helper that decides add/update/ignore. Adds `--dry-run` on
  `learn`, `restore`, `doctor`, keyword fallback when Ollama is down,
  a rewrite-shrink check (rejects rewrites under 50% of old length),
  collision-proof `.history` backups, and a code-level `--yes` gate on
  `restore` (preview without it; refuses to run without it). Shrink check
  and `restore` tested on real runs (2026-10-09). recall/learn behaviour
  is defined in the GHOST.md Memory section and passed testing.

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
- [x] Boot sequence and identity — reads `GHOST.md`, `VAULT-INDEX.md`,
      `Active Priorities.md`, and `Projects\Ghost.md` on boot, correctly
      identifies as Ghost, and detects missing daily notes.
- [x] Overwrite confirmation gate under OpenCode — PASS with
      `GHOST.md` loaded and in context: read the rules, resolved the
      file, read current content, stated the exact change, and waited
      for explicit confirmation before overwriting. Prompt-level gate,
      not a code-level hard lock.
- [x] Memory commands fire unprompted in a fresh session — verified in
      a screenshot: recall ran on its own, semantic search returned
      the correct top hit, startup sequence ran first without being
      asked.
- [x] Multi-step chained tasks — tested 2026-10-15 (multi-tool evidence
      gathering across files in one session, then a coordinated
      multi-edit vault update).
- [ ] Destructive-action confirmation gates beyond overwrite and restore
      — `Vault\Memory\` writes now hard-denied via `opencode.json`
      permissions (verified live 2026-10-15); other destructive actions
      remain prompt-level only.

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

- Auto-loading of `GHOST.md` was previously a critical gap; fixed by
  adding `GHOST.md` to `opencode.json` `"instructions"`. Startup
  sequence now auto-executes.
- `Vault\Memory\` enforcement upgraded from prompt-level to code-level:
  `opencode.json` permissions deny edit/write/patch on `Vault/Memory`
  and `Vault/Memory/**`. Verified live 2026-10-15 — OpenCode itself
  blocked a direct write attempt. The GHOST.md prompt rule remains as
  the second layer.
- A fresh terminal session starts as vanilla OpenCode unless launched
  with the Ghost project/config loaded. Auto-load now works through
  `opencode.json`, but persona adoption still depends on this project
  context being active.
- Restore confirmation gate now exists in code: the CLI refuses without
  `--yes`, and the `restore()` function refuses unless `yes=True`. An
  agent that deliberately passes `--yes` can still bypass it; the
  GHOST.md rule (preview first, separate go-ahead) is the second layer.
- Overwrite confirmation gate under OpenCode: previous FAILED result
  was invalid because `GHOST.md` was not loaded — OpenCode was running
  as vanilla OpenCode. Corrected test with `GHOST.md` loaded PASSED.
  This is prompt-level soft enforcement, not a code-level hard lock;
  still watch for bypasses in future tests.
- Not fully local anymore. Fledge Alpha Free runs on OpenCode's
  servers, not this machine. Accepted tradeoff for now, since it's the
  first setup that actually works end to end — revisit if privacy/
  offline-only becomes a hard requirement. Fledge Alpha's data policy
  is unknown. Assume anything read or recalled is sent to the provider
  and may be retained.
- `obsidian_memory.py` v3.1 still depends on Ollama running with both
  `nomic-embed-text` (for embeddings) and `qwen2.5:3b` (for the
  `learn()` decision step). If the chat model hallucinates JSON, the
  `learn()` fallback still saves the info as a new note — which can
  cause duplicate notes over time.
- Rewrite corruption risk on `learn()` update is mitigated (old
  versions backed up to `.history` with collision-proof names, `restore`
  and `doctor` built, shrink check rejects rewrites under 50% of old
  length). Shrink check and `restore` tested on real runs 2026-10-09
  (`.history` shows repeated update/restore cycles on `favorite-language`).

## Done

- [x] Obsidian installed and linked to the vault.
- [x] `add()` end-to-end through OpenCode with `qwen2.5:3b` and
      `nomic-embed-text`.
- [x] `update()` on a real run — old version backed up to `.history`,
      old fact kept.
- [x] `learn --dry-run` — exists and runs the safety checks.
- [x] `restore` — built and tested; code-level gate: CLI and function
      both refuse without `--yes` / `yes=True` (v3.1).
- [x] `doctor` built.
- [x] Keyword fallback when Ollama is down — confirmed on a real run:
      Ollama off, URLError warning shown, keyword search used, learn
      saved new notes via the fallback.
- [x] Rewrite-shrink check — rejects rewrites under 50% of old length;
      tested on a real run 2026-10-09.
- [x] Memory section live and tested — memory tests passed in a fresh
      session, verified by the user: recall runs on its own; learn runs
      `--dry-run` then asks "Save this?" and saves only after yes; an
      unknown fact gets "not in the vault" with no guess; the restore
      request names the file and waits for a go-ahead.
- [x] `GHOST.md` auto-load — loaded through `opencode.json`
      (`"instructions": ["GHOST.md"]`).
- [x] Startup sequence auto-executes on a fresh session — reads
      `VAULT-INDEX.md`, `Active Priorities.md`, checks daily note,
      then greets with the welcome line.
- [x] Code-level lock on `Vault\Memory\` — `opencode.json` permissions
      deny edit/write/patch on `Vault/Memory` and `Vault/Memory/**`;
      verified live 2026-10-15 when OpenCode itself blocked a direct
      write attempt.

## Not built yet

- [ ] Voice / hands-free layer (wake word, mic input, text-to-speech) —
      the "Tony Stark talking to the room" piece. Not started.
- [ ] Jobs\ folder structure — one master note per recurring task,
      providing the complete skill and context for that task.