"""
obsidian_memory.py v3.1 - safe local long-term memory for Ghost (Ollama + Obsidian vault)

What v3 added over v2 (v3.1 adds the restore --yes gate and collision-proof backups):
  * No pip install needed: uses only the Python standard library (urllib).
  * Works when Ollama is dead: search falls back to keyword (TF-IDF) matching.
  * update() can no longer silently corrupt notes:
        - the old version is backed up to .history/ first
        - rewrites that shrink a note too much are rejected
        - empty rewrites are rejected
        - writes are atomic (temp file, then replace)
  * Duplicates: exact-text duplicates are skipped; broken model output is retried once.
  * --dry-run shows what `learn` WOULD do without writing anything.
  * `restore` undoes a bad update. It refuses to run without --yes, which stops accidental runs
    (an agent that deliberately types --yes can still bypass it; the GHOST.md rule is the second layer).
    `doctor` checks your setup.
  * Embedding cache is reset automatically if you change the embedding model.
  * .history/ is never searched.

Commands:
  python obsidian_memory.py doctor
  python obsidian_memory.py learn "User switched from Python to Rust" --dry-run
  python obsidian_memory.py learn "User switched from Python to Rust"
  python obsidian_memory.py recall "what language does the user like"
  python obsidian_memory.py remember "Title" "Content"
  python obsidian_memory.py restore 2026-10-05-favorite-language.md          (preview only)
  python obsidian_memory.py restore 2026-10-05-favorite-language.md --yes    (actually restore)

Settings (environment variables, all optional):
  GHOST_VAULT_MEMORY   vault folder      (default C:\\ghost\\Vault\\Memory)
  GHOST_CHAT_MODEL     Ollama chat model (default qwen2.5:3b)
  GHOST_EMBED_MODEL    embedding model   (default nomic-embed-text)
  GHOST_OLLAMA_URL     Ollama address    (default http://localhost:11434)
"""

import os
import re
import sys
import json
import math
import shutil
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from collections import Counter

VAULT = os.environ.get("GHOST_VAULT_MEMORY", r"C:\ghost\Vault\Memory")
OLLAMA = os.environ.get("GHOST_OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("GHOST_EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.environ.get("GHOST_CHAT_MODEL", "qwen2.5:3b")

CACHE_NAME = ".embed_cache.json"
HISTORY_DIR = ".history"
MIN_KEEP_RATIO = 0.5      # an update may not shrink a note below 50% of its old length
MAX_EMBED_CHARS = 4000    # keep embedding requests a sane size

try:  # avoid Windows console encoding crashes
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


class UpdateRejected(Exception):
    """Raised when a note rewrite fails a safety check."""


# ======================================================================
# Ollama (standard library only)
# ======================================================================

def _post(endpoint, payload, timeout=120):
    req = urllib.request.Request(
        OLLAMA + endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _get(endpoint, timeout=5):
    with urllib.request.urlopen(OLLAMA + endpoint, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def embed(text, is_query):
    """nomic-embed-text works best with these task prefixes."""
    if "nomic" in EMBED_MODEL:
        text = ("search_query: " if is_query else "search_document: ") + text
    out = _post("/api/embed", {"model": EMBED_MODEL, "input": text[:MAX_EMBED_CHARS]}, timeout=60)
    return out["embeddings"][0]


def chat_json(prompt):
    """format=json forces valid JSON, which small models need. temperature 0 = consistent."""
    out = _post("/api/chat", {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0},
    }, timeout=180)
    return json.loads(out["message"]["content"])


def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


# ======================================================================
# Note files
# ======================================================================

def _slugify(title):
    return re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")[:60] or "note"


def _atomic_write(path, text):
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _body(text):
    """Note text without the --- front matter ---."""
    m = re.match(r"^---\n.*?\n---\n(.*)$", text.replace("\r\n", "\n"), re.S)
    return m.group(1) if m else text


def _title_of(text, path):
    m = re.search(r"^title:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else path.stem


def _load_notes(vault):
    """[(path, text)] for every note, skipping .history."""
    vault = Path(vault)
    if not vault.exists():
        return []
    notes = []
    for p in sorted(vault.rglob("*.md")):
        if HISTORY_DIR in p.relative_to(vault).parts:
            continue
        notes.append((p, p.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")))
    return notes


def remember(vault_dir, title, content):
    """Create a new note. Returns its path."""
    vault = Path(vault_dir)
    vault.mkdir(parents=True, exist_ok=True)
    base = f"{datetime.now():%Y-%m-%d}-{_slugify(title)}"
    path, n = vault / f"{base}.md", 1
    while path.exists():
        path = vault / f"{base}-{n}.md"
        n += 1
    now = datetime.now().isoformat(timespec="seconds")
    _atomic_write(path, f"---\ntitle: {title}\ncreated: {now}\nupdated: {now}\n---\n\n{content.strip()}\n")
    return path


def _backup(vault, path):
    hist = Path(vault) / HISTORY_DIR
    hist.mkdir(exist_ok=True)
    # Microseconds in the name: two backups in the same second must never share a
    # filename, or the newer one would silently overwrite the older (lost) version.
    while True:
        dest = hist / f"{path.stem}__{datetime.now():%Y%m%d-%H%M%S-%f}.md"
        if not dest.exists():
            break
    shutil.copy2(path, dest)
    return dest


def _check_update(path, new_content, force=False):
    new = new_content.strip()
    if not new:
        raise UpdateRejected("empty rewrite")
    old = _body(path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")).strip()
    if not force and old and len(new) < len(old) * MIN_KEEP_RATIO:
        raise UpdateRejected(f"rewrite is only {len(new) * 100 // len(old)}% of the old length")


def update(vault_dir, filename, new_content, new_title=None, force=False):
    """Safely rewrite a note: check, back up, then atomic write. Raises UpdateRejected."""
    vault = Path(vault_dir)
    path = vault / Path(filename).name
    if not path.exists():
        raise UpdateRejected("file does not exist")
    _check_update(path, new_content, force)
    text = path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
    created = re.search(r"^created:\s*(.+)$", text, re.M)
    created = created.group(1).strip() if created else datetime.now().isoformat(timespec="seconds")
    title = new_title or _title_of(text, path)
    now = datetime.now().isoformat(timespec="seconds")
    _backup(vault, path)
    _atomic_write(path, f"---\ntitle: {title}\ncreated: {created}\nupdated: {now}\n---\n\n{new_content.strip()}\n")
    return path


def latest_backup(vault_dir, filename):
    """Path of the most recent backup of a note, or None."""
    vault = Path(vault_dir)
    stem = Path(filename).stem
    backups = sorted((vault / HISTORY_DIR).glob(f"{stem}__*.md"))
    return backups[-1] if backups else None


def restore(vault_dir, filename, yes=False):
    """Put the most recent backup of a note back.

    CODE-LEVEL GATE: the CLI refuses without --yes, and this function refuses unless yes=True
    is passed explicitly. That stops accidental or forgetful callers. A caller that deliberately
    passes yes=True / types --yes bypasses it, so the GHOST.md rule is the second layer.
    Returns the backup used, or None if there is none.
    """
    if not yes:
        raise UpdateRejected("restore refused: confirmation flag (--yes) not given")
    vault = Path(vault_dir)
    target = vault / Path(filename).name
    backup = latest_backup(vault, filename)
    if backup is None:
        return None
    if target.exists():
        _backup(vault, target)  # so the restore itself is undoable
    shutil.copy2(backup, target)
    return backup


# ======================================================================
# Search: embeddings first, keyword fallback
# ======================================================================

def _load_cache(vault):
    f = Path(vault) / CACHE_NAME
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("model") == EMBED_MODEL:
            return data.get("notes", {})
    except Exception:
        pass
    return {}


def _save_cache(vault, notes):
    try:
        (Path(vault) / CACHE_NAME).write_text(
            json.dumps({"model": EMBED_MODEL, "notes": notes}), encoding="utf-8")
    except OSError:
        pass


def _semantic(vault, notes, query, top_k):
    cache, live, vecs, changed = _load_cache(vault), set(), [], False
    for path, text in notes:
        key = str(path.relative_to(vault))
        live.add(key)
        mtime = path.stat().st_mtime
        entry = cache.get(key)
        if not entry or entry["mtime"] != mtime:
            # title first so it counts for more
            entry = {"mtime": mtime, "vec": embed(f"{_title_of(text, path)}\n{_body(text)}", False)}
            cache[key] = entry
            changed = True
        vecs.append(entry["vec"])
    for k in set(cache) - live:
        del cache[k]
        changed = True
    if changed:
        _save_cache(vault, cache)
    qv = embed(query, True)
    scored = [(p, t, cos(qv, v)) for (p, t), v in zip(notes, vecs)]
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]


_TOKEN = re.compile(r"[a-z0-9]+")


def _keyword(notes, query, top_k):
    docs = [_TOKEN.findall(t.lower()) for _, t in notes]
    q = _TOKEN.findall(query.lower())
    df = Counter()
    for d in docs:
        df.update(set(d))
    n = len(docs)

    def vec(tokens):
        if not tokens:
            return {}
        tf = Counter(tokens)
        return {t: (c / len(tokens)) * (math.log((1 + n) / (1 + df.get(t, 0))) + 1) for t, c in tf.items()}

    def cosine(a, b):
        dot = sum(a[t] * b[t] for t in set(a) & set(b))
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    qv = vec(q)
    scored = [(p, t, cosine(qv, vec(d))) for (p, t), d in zip(notes, docs)]
    scored.sort(key=lambda x: x[2], reverse=True)
    return [s for s in scored if s[2] > 0][:top_k]


def recall(vault_dir, query, top_k=3):
    """Returns ([(path, text, score)], mode). mode = 'semantic', 'keyword' or 'none'."""
    vault = Path(vault_dir)
    notes = _load_notes(vault)
    if not notes:
        return [], "none"
    try:
        return _semantic(vault, notes, query, top_k), "semantic"
    except (OSError, KeyError, IndexError, ValueError) as e:
        print(f"[warn] embeddings unavailable ({type(e).__name__}); using keyword search instead.",
              file=sys.stderr)
        return _keyword(notes, query, top_k), "keyword"


# ======================================================================
# The helper: new info -> recall similar -> LLM decides -> add/update/ignore
# ======================================================================

def _norm(s):
    return re.sub(r"\s+", " ", s.lower()).strip()


def _already_saved(vault_dir, info):
    """Exact-text duplicate check (safe: never mistakes a contradiction for a duplicate)."""
    target = _norm(info)
    for p, t in _load_notes(vault_dir):
        if target and target in _norm(_body(t)):
            return p
    return None


def _ask_llm(existing, new_info):
    prompt = f"""You manage a small memory notebook.

EXISTING NOTES:
{existing}

NEW INFO:
{new_info}

Pick ONE action. Reply with JSON only, in exactly this shape:
{{"action": "add", "file": "", "title": "short title", "content": "the note text"}}

Rules:
- "update": the new info changes or extends an existing note. Put that note's filename in "file".
  In "content" write the FULL corrected note and KEEP every old fact that is still true.
  Never shorten the note or drop unrelated facts.
- "ignore": the new info is trivial or already saved. Leave title and content empty.
- "add": anything else worth remembering.
Write content as short, plain facts."""
    for _ in range(2):  # one retry for flaky small models
        try:
            d = chat_json(prompt)
        except (OSError, ValueError, KeyError):
            continue
        if not isinstance(d, dict):
            continue
        action = str(d.get("action", "")).strip().lower()
        if action not in ("add", "update", "ignore"):
            continue
        d = {
            "action": action,
            "file": str(d.get("file") or "").strip(),
            "title": str(d.get("title") or "").strip(),
            "content": str(d.get("content") or "").strip(),
        }
        if action == "update" and not d["content"]:
            continue
        return d
    return None


def _add(vault_dir, title, content, dry_run, reason):
    if dry_run:
        return {"action": "add", "file": "(new note)", "reason": reason + " [dry run - nothing written]",
                "title": title, "content": content}
    path = remember(vault_dir, title, content)
    return {"action": "add", "file": path.name, "reason": reason}


def learn(vault_dir, new_info, dry_run=False, force=False):
    """Decide whether new info should be added, update a note, or be ignored. Returns a dict."""
    new_info = new_info.strip()
    if not new_info:
        return {"action": "ignore", "reason": "empty input"}

    dup = _already_saved(vault_dir, new_info)
    if dup:
        return {"action": "ignore", "file": dup.name, "reason": "exact text already saved"}

    similar, _mode = recall(vault_dir, new_info, top_k=3)
    existing = "\n\n".join(f"[{p.name}]\n{_body(t).strip()}" for p, t, _ in similar) or "(none)"

    d = _ask_llm(existing, new_info)
    if d is None:
        return _add(vault_dir, new_info[:40], new_info, dry_run,
                    "model gave an unusable answer twice; saved as a new note so nothing is lost")

    if d["action"] == "ignore":
        return {"action": "ignore", "reason": "model judged it trivial or already saved"}

    if d["action"] == "update":
        target = {p.name: p for p, _, _ in similar}.get(d["file"])
        if target is None:
            return _add(vault_dir, new_info[:40], new_info, dry_run,
                        "model named a file that does not exist; saved as a new note")
        try:
            _check_update(target, d["content"], force)
        except UpdateRejected as e:
            return _add(vault_dir, new_info[:40], new_info, dry_run,
                        f"update rejected ({e}); saved as a new note, old note untouched")
        if dry_run:
            return {"action": "update", "file": target.name, "content": d["content"],
                    "reason": "passed safety checks [dry run - nothing written]"}
        update(vault_dir, target.name, d["content"], None, force)
        return {"action": "update", "file": target.name, "reason": "old version backed up to .history/"}

    # Save the exact new info AND build the title from it. Small models mix in facts
    # from other notes and even copy placeholder text (e.g. "short title") from the prompt.
    return _add(vault_dir, new_info[:50], new_info, dry_run, "model chose to add")


# ======================================================================
# doctor + CLI
# ======================================================================

def doctor(vault_dir):
    ok = True
    print(f"Vault folder : {vault_dir}  ({'exists' if Path(vault_dir).exists() else 'will be created on first save'})")
    print(f"Ollama URL   : {OLLAMA}")
    try:
        names = [m["name"] for m in _get("/api/tags").get("models", [])]
        print("Ollama       : running")
    except Exception as e:
        print(f"Ollama       : NOT reachable ({type(e).__name__}). Start the Ollama app or run: ollama serve")
        print("               (keyword search still works without it)")
        return False
    for label, model in (("Embed model", EMBED_MODEL), ("Chat model", CHAT_MODEL)):
        found = any(n == model or n.split(":")[0] == model or n.startswith(model + ":") for n in names)
        print(f"{label:<13}: {model}  -> {'found' if found else 'MISSING, run: ollama pull ' + model}")
        ok = ok and found
    return ok


def _cli():
    ap = argparse.ArgumentParser(prog="obsidian_memory", description="Safe local memory for Ghost.")
    ap.add_argument("--vault", default=VAULT)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="Check Ollama, models and vault.")

    r = sub.add_parser("remember", help="Save a note directly.")
    r.add_argument("title")
    r.add_argument("content")

    ln = sub.add_parser("learn", help="Let the model decide add / update / ignore.")
    ln.add_argument("info")
    ln.add_argument("--dry-run", action="store_true", help="Show the decision, write nothing.")
    ln.add_argument("--force", action="store_true", help="Allow rewrites that shrink a note a lot.")

    q = sub.add_parser("recall", help="Find relevant notes.")
    q.add_argument("query")
    q.add_argument("--top-k", type=int, default=3)

    rs = sub.add_parser("restore", help="Undo the last update of a note (needs --yes).")
    rs.add_argument("filename")
    rs.add_argument("--yes", action="store_true",
                    help="Required to actually restore. Without it, only a preview is shown.")

    a = ap.parse_args()

    if a.cmd == "doctor":
        print("\nAll good." if doctor(a.vault) else "\nFix the items above, then run doctor again.")
    elif a.cmd == "remember":
        print("Saved:", remember(a.vault, a.title, a.content))
    elif a.cmd == "learn":
        res = learn(a.vault, a.info, dry_run=a.dry_run, force=a.force)
        print(f"Action : {res['action']}")
        if res.get("file"):
            print(f"File   : {res['file']}")
        print(f"Reason : {res['reason']}")
        if a.dry_run and res.get("content"):
            print(f"Would write:\n{res['content']}")
    elif a.cmd == "restore":
        backup = latest_backup(a.vault, a.filename)
        if backup is None:
            print("No backup found for that note.")
            sys.exit(1)
        if not a.yes:
            print(f"PREVIEW ONLY - nothing was changed.")
            print(f"Note   : {Path(a.filename).name}")
            print(f"Backup : {backup.name}")
            print("Restoring replaces the note with that backup (the current version is backed up first).")
            print("To go ahead, run the same command again with --yes")
            sys.exit(2)
        used = restore(a.vault, a.filename, yes=True)
        print(f"Restored from {used.name}")
    else:
        results, mode = recall(a.vault, a.query, a.top_k)
        if not results:
            print("No relevant notes found.")
        else:
            print(f"(search mode: {mode})")
        for p, t, s in results:
            print(f"\n--- {p.name} (score: {s:.2f}) ---\n{_body(t).strip()}")


if __name__ == "__main__":
    _cli()