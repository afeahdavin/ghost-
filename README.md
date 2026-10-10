# Ghost

A personal AI operator that lives on your own computer — reads files, writes files, remembers you between sessions, and follows a written rulebook.

This repo is the complete build: the memory system, the rules, the boot config, and the vault it lives in. It is the actual working system, not a demo.

---

## What Ghost is

Ghost is an AI assistant with four parts:

- **A brain** — a language model that thinks and understands.
- **Hands** — the ability to actually open files, write notes, and run commands, not just talk about it.
- **A memory** — a folder of plain text notes Ghost reads from and writes to, so it remembers you when the session closes.
- **Rules** — a boot file that tells Ghost who it is, how to behave, and what it is never allowed to do.

Ghost runs inside **OpenCode** (a command-line AI tool) and uses a cloud model for its brain. It boots fresh every session and loads its memory from the vault.

---

## The folder layout
