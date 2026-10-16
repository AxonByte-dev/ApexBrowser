# Apex Core - Secure Workstation Browser

Apex Core is a high-performance, multi-tabbed desktop web browser workstation powered by a hardware-accelerated **Chromium** rendering engine architecture. Built to securely inspect untrusted web components, it features a native, real-time heuristics engine that intercept traffic loops, a persistent SQLite transaction database, and strict system-level Cloudflare privacy DNS routing overrides.

## Key Architecture & Features

- **Isolated Chromium Pipeline:** Deploys a dedicated multi-threaded rendering core via `PyQt6.QtWebEngineWidgets` with persistent disk caching and session cookie state tracking.
- **Real-Time Heuristic Firewall:** Scans all runtime navigation and background link redirects before execution. Instantly terminates threat pipelines matching deep subdomain routing tricks, stacked routing configurations, or embedded credential phishing keywords.
- **Cloudflare DNS Privacy Lock:** Bypasses default local Windows system or router network adapters at boot. Appends `--built-in-dns-lookup-enabled` flags directly into the Chromium execution layer to route all domain allocations securely through `1.1.1.1` and `1.0.0.1`.
- **Relational History Ledger:** Archives clean, validated web visits into an on-disk, thread-safe local **SQLite3** database instance.

## Installation & Deployment

### For General Users
1. Head over to the **Releases** widget on the right side of this repository.
2. Download the packaged deployment block: `ApexBrowser-v1.1-Windows.zip`.
3. Extract the ZIP directory structure anywhere onto your machine.
4. Run the native executable launcher: `ApexBrowser.exe`.

### For Developers (Running from Source)
Ensure you have Python installed, clone the repository, and acquire the binary engine components via pip:
```bash
pip install PyQt6 PyQt6-WebEngine
python production_secure_browser.py
```

### Compiling and Bundling the Distribution Engine
To compile the source pipeline back into a standalone directory layout using PyInstaller, execute:
```powershell
python -m PyInstaller --noconfirm --onedir --windowed --add-data "browser_history.db;." --icon="app_icon.ico" --name "ApexBrowser" production_secure_browser.py
```
*Note: Ensure to strip/delete any existing `browser_history.db` tracking logs from the final `dist/ApexBrowser/` directory before compression to avoid distributing personal data.*

## Security & Architecture Disclaimer
Apex Core is an educational security-focused environment browser engineered to demonstrate client-side network intercept patterns and heuristic analysis filters. It should be run in standard local sandboxes when inspecting hazardous domains.
