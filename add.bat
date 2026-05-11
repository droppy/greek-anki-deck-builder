@echo off
set FORCE_FLAG=
if "%~2"=="1" set FORCE_FLAG=--force-add
python -m greek_anki add %1 --apkg "AZ greek words.apkg" --no-review --freq-db freq_list.sq3 %FORCE_FLAG%
