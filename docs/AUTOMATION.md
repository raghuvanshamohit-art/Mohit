# Automating the daily 8 PM scan

The VCP screener is an **End-Of-Day** tool: run it once a day after the market
closes. NSE publishes the bhavcopy around **6–7 PM IST**, so **8 PM IST** is a
safe slot. NSE trades **Mon–Fri**, so schedule it on weekdays.

Each run writes `output/vcp_fno_<timestamp>.{csv,html}` and refreshes
`output/latest.html` / `output/latest.csv` so you always have a stable link to
the newest board.

> **Timezone.** Cron/Task Scheduler fire in the **machine's local time**.
> - Machine clock already on **IST** → schedule for **20:00**.
> - Server on **UTC** → 8 PM IST = **14:30 UTC**.

---

## One-time setup

```bash
git clone <your-fork-url> Mohit && cd Mohit
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_screener.py              # first run backfills ~2 years into cache/bhav
```

The runner scripts auto-activate `.venv` if it sits at the repo root, so create
it there.

---

## Linux / macOS — cron

Make the runner executable, then add a crontab entry:

```bash
chmod +x tools/daily_run.sh
crontab -e
```

Add **one** of these lines (weekdays):

```cron
# Machine clock on IST -> 8:00 PM local
0 20 * * 1-5 /full/path/to/Mohit/tools/daily_run.sh

# Server on UTC -> 8:00 PM IST = 14:30 UTC
30 14 * * 1-5 /full/path/to/Mohit/tools/daily_run.sh
```

Check it ran: `tail -f /full/path/to/Mohit/logs/vcp_*.log`.

---

## Linux — systemd timer (more robust than cron)

`~/.config/systemd/user/vcp-screener.service`:

```ini
[Unit]
Description=VCP F&O screener (daily EOD)

[Service]
Type=oneshot
WorkingDirectory=%h/Mohit
ExecStart=%h/Mohit/tools/daily_run.sh
```

`~/.config/systemd/user/vcp-screener.timer`:

```ini
[Unit]
Description=Run the VCP F&O screener at 8 PM IST on weekdays

[Timer]
# OnCalendar is in the system timezone. Use 20:00 if that's IST, else 14:30 for UTC.
OnCalendar=Mon..Fri 20:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now vcp-screener.timer
systemctl --user list-timers vcp-screener.timer
```

(For a machine that isn't always logged in, `sudo loginctl enable-linger $USER`
so user timers run headless — or install the units under `/etc/systemd/system/`.)

---

## macOS — launchd (alternative to cron)

`~/Library/LaunchAgents/com.vcp.screener.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.vcp.screener</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/YOU/Mohit/tools/daily_run.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
  </array>
</dict></plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.vcp.screener.plist
```

---

## Windows — Task Scheduler

From an elevated Command Prompt (adjust the path; `/st 20:00` = 8 PM local):

```bat
schtasks /Create /TN "VCP F&O Screener" ^
  /TR "C:\path\to\Mohit\tools\run_daily.bat" ^
  /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 20:00 /RL LIMITED /F
```

Verify / run on demand:

```bat
schtasks /Query /TN "VCP F&O Screener"
schtasks /Run   /TN "VCP F&O Screener"
```

---

## Running it in the cloud instead

The runner needs outbound access to `archives.nseindia.com`. Managed/sandboxed
environments (including this Claude Code web environment) often block that host
by network policy, so a nightly job there would fetch nothing. To run in the
cloud, use a host/VM whose network allows NSE, then apply the cron/systemd setup
above. (In Claude Code on the web, that means an environment whose network policy
permits `archives.nseindia.com`.)
