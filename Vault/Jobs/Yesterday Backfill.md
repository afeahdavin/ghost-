# Yesterday Backfill

**Runs:** daily

**Trigger:** startup sequence, when yesterday's daily note is missing or thin

**Purpose:** no day silently disappears from the record.

**Steps:**

1. Locate yesterday's note: `Vault\01 - Daily Notes\NN - Month YYYY\YYYY-MM-DD.md` (yesterday's real date).
2. If the file is missing, reconstruct what's knowable from context (project notes, prior daily notes, file modification evidence) — never invent events.
3. Create the note with correct frontmatter and an honest status line (e.g. reconstructed, partial, gap).
4. If nothing can be reconstructed, create the note saying the day is an unexplained gap.
5. Report the backfill to the user.

**Files involved:**

- `Vault\01 - Daily Notes\NN - Month YYYY\YYYY-MM-DD.md` (yesterday's)

**Done looks like:**

- Yesterday's file exists.
- Anything written is sourced or explicitly marked as unknown — no fabricated activity.
- User informed of what was backfilled vs. what remains a gap.
