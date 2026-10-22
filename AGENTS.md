# AGENTS.md - Bing Rewards Automation v2 Context Guide

## Tech Stack
- **Language & Runtime:** Python 3.12+ (Virtualenv at `Bing.v2/venv/`)
- **Automation Framework:** Selenium WebDriver 4.44+ with `webdriver-manager`
- **Target Browser:** Microsoft Edge (Chromium-based, Windows x64)
- **Protocol:** Chrome DevTools Protocol (CDP) for mobile device metrics and touch emulation
- **Test Suite:** Python built-in `unittest`
- **Shell / Launcher:** Windows Batch (`run.bat`) with UTF-8 codepage (`chcp 65001`)

---

## Commands
- **Launch Tool (User entry point):** Double-click `run.bat` (available at root or `Bing.v2/run.bat`)
- **Direct Script Execution:** `.\Bing.v2\venv\Scripts\python.exe Bing.v2\bing_auto.py`
- **Run All Automated Tests (15 tests):**
  ```powershell
  .\Bing.v2\venv\Scripts\python.exe -m unittest discover -s ".\Bing.v2\tests"
  ```
- **Install / Update Dependencies:**
  ```powershell
  .\Bing.v2\venv\Scripts\python.exe -m pip install -r Bing.v2\requirements.txt
  ```

---

## Directory Architecture
```
Bing.v2/ (Workspace Root)
├── AGENTS.md                  ← This context & rules document
├── run.bat                    ← Root launcher forwarding to Bing.v2\run.bat
├── PRD.txt                    ← Core product requirements
├── tasks/                     ← Implementation plans & checklists
│   ├── plan.md
│   └── todo.md
├── Sample/                    ← Legacy/backup reference code
└── Bing.v2/                   ← Active Production Codebase
    ├── run.bat                ← Main setup & runner script
    ├── config.py              ← Central settings, constants, and console UI helpers
    ├── popup_handler.py       ← Bing cookie & privacy consent dialog cleaner
    ├── bing_auto.py           ← Search orchestrator, CDP switcher, points auditor
    ├── requirements.txt       ← Python dependencies (selenium, webdriver-manager, faker)
    ├── README.md              ← Vietnamese end-user manual
    ├── edge_profile/          ← Persistent Edge user profile (keeps MSA login session)
    ├── keywords.txt           ← Temporary file holding generated search terms
    └── tests/                 ← Unittest test suite
        ├── test_config.py
        ├── test_popup_handler.py
        ├── test_automation.py
        └── test_e2e_search.py
```

---

## Core Domain Rules & Gotchas

### 1. Microsoft Rewards 15-Minute Cooldown & Search Limits
- **Daily Caps (Gold Member / VN):**
  - Desktop Bing search: `90 / 90` points (30 searches @ 3 pts).
  - Mobile Bing search: `60 / 60` points (20 searches @ 3 pts).
- **Anti-Abuse Cooldown Window & Batching Solution:**
  Microsoft limits accounts to **3–4 searches (~9–12 points) per 15-minute block**. If searches are sent continuously without waiting (e.g. 30 PC then immediately 20 Mobile), the entire second batch will yield 0 points.
  - Solution: Batch searches in chunks of `BATCH_SEARCH_COUNT = 4`.
  - In Auto-Cooldown mode (`--auto` / Option 1), the runner sleeps 15 minutes (`COOLDOWN_SECONDS = 915`) with a live interactive countdown timer, repeating automatically until reaching 100% daily points.
- **Mobile Viewport & DOM Integrity:**
  - Before each search: Always call `window.scrollTo({top: 0, behavior: 'instant'});` so `#sb_form_q` is never scrolled off-screen.
  - Prevent double submission: Decode URLs using `urllib.parse.unquote_plus(driver.current_url)` to avoid false mismatch triggers from `%20` vs `+` encoding.
- **Dwell Time & Interaction Requirement:**
  Bing requires user interaction on the search results page (2-way touch scrolling down 280–480px, pausing 1.5–2.5s, scrolling back 60–160px, returning to top, and maintaining 7–12s total interval) for telemetry beacons (`/rewards/`) to credit points.

### 2. Live Points Audit (`get_rewards_breakdown`)
- The homepage `rewards.bing.com` only displays `Search: 1/1` (Daily Streak).
- The true breakdown (`90/90`, `42/60`) is found under the **"Points breakdown"** modal on `https://rewards.bing.com/earn`.
- The tool reads this modal dynamically on startup, after every batch, and upon completion:
  - If PC is already 90/90, it automatically skips PC searches to save time.
  - If Mobile is partially completed (e.g. 42/60), it only generates and runs the remaining searches needed.

### 3. Persistent Profile Management
- The persistent profile path is `Bing.v2/edge_profile/`.
- **CRITICAL:** Never wipe or delete `edge_profile/Default/Network/Cookies`. It holds the authenticated `.MSA.Auth` session token.
- Pass `--user-data-dir` and `--profile-directory=Default` explicitly to Edge options.

### 4. Overlay & Popup Handling
- Mobile Bing displays `#bnp_cookie_banner` and `<div class="bnp_overlay_wrapper"></div>`.
- If not dismissed, this modal backdrop intercepts all clicks on `#sb_form_q` (`ElementClickInterceptedException`).
- `popup_handler.py` automatically dismisses and removes `.bnp_overlay_wrapper` and related dialogs before and after every search.

### 5. Windows Batch Scripting Pitfalls
- **Parentheses in `else (...)` blocks:** In `cmd.exe`, any unescaped closing parenthesis `)` inside `echo (...)` will prematurely terminate the `else` block, producing `xxx was unexpected at this time.` syntax errors.
- **Virtualenv Activation:** Avoid `activate.bat` when possible; invoke `venv\Scripts\python.exe` directly to prevent `chcp.com` parsing bugs on non-English Windows consoles.

---

## Coding Standards & Conventions
- **Language & Encoding:** Python 3 with explicit UTF-8 stdout reconfiguration on Windows.
- **Paths:** Always resolve paths dynamically using `os.path.abspath(os.path.dirname(__file__))`. Never use relative working-directory assumptions.
- **Fail-Safe Fallbacks:**
  - For browser searches: Try natural DOM interaction (focus, click, typing, Enter). If DOM is obscured, fall back to JavaScript click or direct URL navigation (`https://www.bing.com/search?q=...&form=QBRE`).
- **Preservation:** Maintain existing comments, test suites, and documentation integrity.
