# Project: PS4 Controller Input Lag

Measuring and reducing DualShock 4 input lag on this PC, specifically the
gap between controller 1 and controller 2.

Script: `C:\Users\afeah\Desktop\PES 2025\ps4_controller_lowlag.py`
Launcher: `C:\ghost\run_ps4_controller_elevated.cmd` (Python 3.10)

## What it is

A **benchmark / diagnostic**, not an in-game fix. It polls the pads through
SDL and reports per-pad software latency. PES itself does not use SDL, so
none of the SDL environment hints in this script affect the game.

## What's in it (rewritten 2026-10-16)

1. Every connected pad is opened and polled — incremental hotplug sync,
   no hard-coded index 0.
2. Process priority: `--priority normal|high|realtime` (default high) via
   `SetPriorityClass`, plus `timeBeginPeriod(1)` for 1 ms timer granularity.
3. Per-pad telemetry: poll rate, worst read gap (software lag ceiling),
   time since last input change, live stick/button readout.
4. `--driver hidapi|dinput` — A/B tests the global
   `SDL_HINT_JOYSTICK_HIDAPI_PS4` hint, which can favour one pad at the
   other's expense.
5. `--duration N` — timed run that dumps a per-pad summary and names the
   laggy pad.

## Measured results (2026-10-16, both pads connected)

| Metric | Before | After |
| --- | --- | --- |
| Loop rate | 18 Hz | ~22,000 Hz |
| Worst loop time | ~60–75 ms | 0.26–0.53 ms |
| Per-pad worst read gap | — | 0.38–0.68 ms |
| Pads polled | 1 (index 0 only) | 2 |

Verified on Python 3.14 + pygame-ce 2.5.8 (SDL 2.32.10) and on Python
3.10 + pygame 2.6.1 (SDL 2.28.4) — the second is what the launcher uses.

## Root causes found

- Old script opened `Joystick(0)` only: controller 2 was never polled.
- `pygame.joystick.quit()/init()` inside the hotplug handler re-queued
  `JOYDEVICEADDED`, re-triggering the handler → infinite 18 Hz rebuild
  loop. Fixed with incremental `sync_pads()`.
- `SetPriorityClass` failed with `ERROR_INVALID_HANDLE(6)` because
  `GetCurrentProcess` returned a truncated int handle. Fixed with
  `restype = c_void_p`.

## Reality check (important)

Software polling is now even across both pads at well under 1 ms. Any lag
that remains in-game is **not** in this software path. Remaining suspects,
in order:

1. Bluetooth vs wired — DS4 BT HID polling is capped far below USB. Wire
   both pads.
2. The game's own input path / frame pacing.
3. Windows USB polling rate for the pad's USB controller.

## Open

- [ ] Run the game with BOTH pads wired and confirm pad-2 lag is gone.
- [ ] If lag persists wired, capture in-game evidence and revisit.
