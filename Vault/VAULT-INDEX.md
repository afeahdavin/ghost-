# VAULT-INDEX.md

This is the map of the vault. It tells Ghost who the user is, where the rules live, and where everything else can be found.

## User profile

- Name: (fill in)
- Preferred tone: direct, vulgar, butler-polished — see GHOST.md
- Preferred address: "sir" or "boss"

## Where the rules live

- Boot config: `C:\ghost\GHOST.md`
- Safety rules: in GHOST.md, "The rules that can't lapse"

## Human Interface

Obsidian is installed and pointed at `C:\ghost\Vault`. It is the primary way the human browses, reads, and edits the vault. The AI reads/writes raw markdown files directly. Obsidian is not required for the AI to function, but it is required for the human to comfortably manage the memory.

## Vault layout

- `01 - Daily Notes\` — one note per day, monthly subfolders (`NN - Month YYYY`), filename `YYYY-MM-DD.md`
- `Projects\` — one note per ongoing project. Currently: `Ghost.md`
- `Memory\` — long-term notes written by `obsidian_memory.py`
- `Active Priorities.md` — live list of open work

## Startup checklist

1. Read this file.
2. Read `Active Priorities.md`.
3. Read yesterday's daily note if it exists.
4. Read `Projects\Ghost.md` if the work touches the Ghost build itself.