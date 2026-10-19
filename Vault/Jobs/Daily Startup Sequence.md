# Daily Startup Sequence

**Runs:** daily

**Trigger:** start of every OpenCode session (GHOST.md boot config)

**Purpose:** load the vault map and current open work before doing anything else.

**Steps:**

1. Read `Vault\VAULT-INDEX.md` — profile, rules, system map.
2. Check yesterday's daily note in `Vault\01 - Daily Notes\`; if Ghost has context it's missing, backfill it.
3. Scan `Vault\Active Priorities.md` for what's currently open, so nothing queued slips.
4. Report the welcome line plus anything the startup found (missing daily note, stale priorities).

**Files involved:**

- `Vault\VAULT-INDEX.md`
- `Vault\Active Priorities.md`
- `Vault\01 - Daily Notes\NN - Month YYYY\YYYY-MM-DD.md` (yesterday's)

**Done looks like:**

- All three files read in full this session.
- Yesterday's daily note existence confirmed; gap flagged (or backfilled) if missing.
- Open priorities reported, none silently forgotten.
