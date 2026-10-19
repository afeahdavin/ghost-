# Project: PES Boost

Performance booster for PES 2025 (PES Professionals Patch). The script
`pes_boost_loop.py` lives in `C:\Users\afeah\Desktop\PES 2025\`.

## What the script does

1. Sets Windows power plan to High Performance (`powercfg /setactive SCHEME_MIN`).
2. Kills background apps once: OneDrive, Discord, Skype, Teams, Chrome, Edge,
   Opera, steamwebhelper.
3. Launches `PES Professionals Patch Launcher.exe`.
4. Waits for the game process, then pins **all** matching PES processes to High
   CPU priority (launcher and game process are separate).
5. Loops every 5 min: cleans `%TEMP%` / `%TMP%` / `C:\Windows\Temp`, re-asserts priority.
6. Auto-stops when PES closes.

## Launchers

- One-click: `C:\Users\afeah\Desktop\PES Boost Loop.bat` — self-elevates, then
  calls the canonical command file. This is the thing to double-click.
- Canonical command (single source of truth): `C:\ghost\run_pes_boost_elevated.cmd`
  — uses Python310, runs `-u` (unbuffered), logs to the PES folder. Not
  self-elevating by design; invoke from an elevated context.
- Logs: `pes_boost_loop.out.log` / `pes_boost_loop.err.log` in the PES 2025 folder.

## Bugs fixed 2026-10-16

1. **The loop crashed every run.** `clean_temp_files()` walked directories with
   `os.walk`, which yields filename *strings*, then called `.stat()` on them →
   `AttributeError: 'str' object has no attribute 'stat'`. Confirmed dead in
   `pes_boost_loop.err.log` (2026-10-14, first 5-minute cleanup). One bad cycle
   now logs and continues instead of killing the loop.
2. **Only the launcher got High priority.** The old code took the first matching
   process (`PES Professionals Patch Launcher.exe`) and stopped. Now matches
   `PES_PROCESS_PATTERNS` (`professionals patch`, `pro evolution soccer`,
   `pes2017`) and boosts **all** matches, re-asserted each cycle.
3. **The loop never boosted itself.** Added self-priority HIGH and an
   elevation-report line at startup.

## Critical

- Requires Administrator. A non-elevated launch crashes at PES startup with
  `OSError [WinError 740] The requested operation requires elevation`. Elevation
  is also needed for `powercfg`, terminating other processes, and cleaning
  `C:\Windows\Temp`.

## Open

- [ ] Verify logs actually populate on the next run (added `-u` 2026-10-12;
  pre-fix logs were consistently 0 bytes).
