@echo off
REM Daily VCP F&O screener runner for Windows Task Scheduler (8 PM IST).
REM Writes timestamped reports to output\, updates output\latest.*, logs to logs\.
setlocal enabledelayedexpansion

set "REPO_DIR=%~dp0.."
cd /d "%REPO_DIR%"

if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"

if not exist logs mkdir logs
if not exist output mkdir output

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
set "STAMP=%DT:~0,8%_%DT:~8,6%"
set "LOG=logs\vcp_%STAMP%.log"

if "%VCP_PROVIDER%"=="" set "VCP_PROVIDER=bhavcopy"

echo [%date% %time%] starting VCP F&O screener (provider=%VCP_PROVIDER%) >> "%LOG%"
python run_screener.py --provider %VCP_PROVIDER% --cache-dir cache\bhav --output-dir output --min-passed 13 %VCP_EXTRA_ARGS% >> "%LOG%" 2>&1
set "STATUS=%ERRORLEVEL%"

REM Copy the newest reports to latest.*
for /f "delims=" %%F in ('dir /b /o-d output\vcp_fno_*.html 2^>nul') do (
  copy /y "output\%%F" "output\latest.html" >nul
  goto :gotHtml
)
:gotHtml
for /f "delims=" %%F in ('dir /b /o-d output\vcp_fno_*.csv 2^>nul') do (
  copy /y "output\%%F" "output\latest.csv" >nul
  goto :gotCsv
)
:gotCsv
echo [%date% %time%] finished (exit=%STATUS%) >> "%LOG%"
endlocal & exit /b %STATUS%
