@echo off
title Ghost Boot Sequence
cd /d C:\ghost

echo ========================================
echo   BOOTING GHOST...
echo   Working directory: C:\ghost
echo ========================================
echo.
echo 1. OpenCode is launching...
echo 2. Paste this into the prompt: 
echo.
echo    Read C:\ghost\GHOST.md in full. You are Ghost.
echo.
echo ========================================

opencode
pause