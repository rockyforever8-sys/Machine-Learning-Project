# Windows quick start (no Git Bash required)

## Launch the dashboard

1. Open **File Explorer**
2. Go to your project folder:  
   `...\Machine-Learning-Project\manufacturing-quality`
3. **Double-click** `run-dashboard.bat`
4. Wait for "Installing streamlit..." then your browser opens at `http://localhost:8501`

You do **not** need Git Bash for the dashboard.

## If double-click fails

Open **Command Prompt** (Win+R → type `cmd` → Enter), then:

```cmd
cd /d "C:\Users\kamyuen wong\OneDrive - JE\Desktop\BUDGET FY2627\MIT Applied Agentic\PPAP Agentic\Machine-Learning-Project\manufacturing-quality"

py -m pip install --user streamlit pypdf
py -m streamlit run dashboard\app.py
```

If `py` is not found, use `python` instead of `py`.

## Why Git Bash showed "No module named streamlit"

Your `pip install` only reported `pypdf` — likely because:

1. **Old code** — pull latest: `git pull` in the repo (or re-download ZIP)
2. **Streamlit not installed** — the `.bat` file installs it explicitly with `--user`

## OneDrive inbox path

In the dashboard sidebar, confirm:

`C:\Users\kamyuen wong\OneDrive - JE\Desktop\BUDGET FY2627\MIT Applied Agentic\PPAP Agentic\PPAP Inbox`

Then click **Run triage now**.
