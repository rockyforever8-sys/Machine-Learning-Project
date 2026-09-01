# Windows quick start (no Git Bash required)

## If localhost:8501 refuses connection

1. Double-click **`diagnose-dashboard.bat`** — shows what is broken
2. Double-click **`Start PPAP Dashboard.vbs`** — starts server, waits until ready, then opens browser
3. Keep the **black terminal window open** while using the dashboard
4. If browser still fails, manually open: **http://127.0.0.1:8501**

## Launch the dashboard

| File | Purpose |
|------|---------|
| **`Start PPAP Dashboard.vbs`** | Start dashboard (recommended) |
| `diagnose-dashboard.bat` | Check Python / streamlit / PPAP module |
| `run-dashboard.bat` | Same as VBS, opens terminal |

## Manual start (Command Prompt)

```cmd
cd /d "C:\Users\kamyuen wong\OneDrive - JE\Desktop\BUDGET FY2627\MIT Applied Agentic\PPAP Agentic\Machine-Learning-Project\manufacturing-quality"

"C:\Program Files\Python313\python.exe" -m pip install --user streamlit pypdf
"C:\Program Files\Python313\python.exe" launch_dashboard.py
```

Then open **http://127.0.0.1:8501** in Chrome.

## Missing launch_dashboard.py

If the terminal says:

```text
can't open file '...\manufacturing-quality\launch_dashboard.py': [Errno 2] No such file or directory
```

this folder is incomplete (old copy or OneDrive did not sync). From Git Bash:

```bash
cd "/c/Users/kamyuen wong/OneDrive - JE/Desktop/BUDGET FY2627/MIT Applied Agentic/PPAP Agentic/Machine-Learning-Project"
git checkout main
git pull
explorer manufacturing-quality
```

Confirm these files exist in `manufacturing-quality`:

- `Start PPAP Dashboard.vbs`
- `run-dashboard.bat`
- `launch_dashboard.py`
- `dashboard\app.py`

Then double-click `Start PPAP Dashboard.vbs` again.

Temporary workaround if `dashboard\app.py` is already there:

```cmd
cd /d "C:\Users\kamyuen wong\OneDrive - JE\Desktop\BUDGET FY2627\MIT Applied Agentic\PPAP Agentic\Machine-Learning-Project\manufacturing-quality"
"C:\Program Files\Python313\python.exe" -m streamlit run dashboard\app.py --server.port 8501 --server.address 127.0.0.1
```

Then open **http://127.0.0.1:8501**.

## Application Control / pyarrow blocked

If you see:

```text
ImportError: DLL load failed while importing lib: An Application Control policy has blocked this file.
```

your corporate Windows policy is blocking **pyarrow** (used by Streamlit's interactive `st.dataframe`). The dashboard now uses a plain HTML table instead and does not require pyarrow.

Update to the latest code:

```bash
git pull
```

Then restart the dashboard: **close the black terminal window fully**, then double-click `Start PPAP Dashboard.vbs` again. Streamlit can keep an old Python module in memory if you only refresh the browser.

## Git pull conflict fix

If `git pull` says `run-dashboard.bat` would be overwritten:

```bash
mv manufacturing-quality/run-dashboard.bat manufacturing-quality/run-dashboard.bat.old
git pull
```
