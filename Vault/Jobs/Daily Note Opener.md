# Daily Note Opener

**Runs:** daily

**Trigger:** first action of each session, after the startup sequence

**Purpose:** guarantee today's daily note exists before any session activity is recorded.

**Steps:**

1. Compute today's date; verify it against the system clock before writing it anywhere.
2. Check `Vault\01 - Daily Notes\NN - Month YYYY\` for `YYYY-MM-DD.md`.
3. If missing, create it with YAML frontmatter: `---\ndate: YYYY-MM-DD\n---`.
4. If the month subfolder doesn't exist yet, create it (`NN - Month YYYY`).

**Files involved:**

- `Vault\01 - Daily Notes\NN - Month YYYY\YYYY-MM-DD.md`

**Done looks like:**

- Today's note exists with correct frontmatter and correct month folder.
- Filename date matches the actual system date, not an assumed one.
