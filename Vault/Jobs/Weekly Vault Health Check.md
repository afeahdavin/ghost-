# Weekly Vault Health Check

**Runs:** weekly

**Trigger:** once a week, or on request

**Purpose:** keep the vault map true and the structure clean.

**Steps:**

1. List every folder in `Vault\` and confirm each has a current index note (or belongs on the update list).
2. Compare folder contents against `VAULT-INDEX.md` — new, renamed, moved, or deleted items must be reflected there.
3. Spot orphan files (no folder index references them) and dead references (indexes pointing at files that don't exist).
4. Fix trivial drift directly; anything structural or ambiguous gets reported to the user first.
5. Append a one-line result to the current daily note.

**Files involved:**

- `Vault\VAULT-INDEX.md`
- Every folder's index note
- `Vault\01 - Daily Notes\NN - Month YYYY\YYYY-MM-DD.md` (today's, for the log line)

**Done looks like:**

- Every folder's index matches the actual contents on disk.
- `VAULT-INDEX.md` layout section is current.
- No orphan files or dead references remain unreported.
- Result logged in today's daily note.
