# Windows quick start (no Git Bash required)

## Launch the dashboard

### Recommended: double-click one of these

| File | What it does |
|------|----------------|
| **`Start PPAP Dashboard.vbs`** | Opens a visible terminal + browser (most reliable) |
| `run-dashboard.bat` | Same, auto-opens a terminal window |

Your browser should open at: **http://localhost:8501**

### If nothing happens

1. Double-click **`Start PPAP Dashboard.vbs`** instead of the `.bat` file
2. Read **`dashboard-launch.log`** in the same folder for error details
3. Or open **Command Prompt** and run:

```cmd
cd /d "C:\Users\kamyuen wong\OneDrive - JE\Desktop\BUDGET FY2627\MIT Applied Agentic\PPAP Agentic\Machine-Learning-Project\manufacturing-quality"

"C:\Program Files\Python313\python.exe" -m pip install --user streamlit pypdf
"C:\Program Files\Python313\python.exe" -m streamlit run dashboard\app.py
```

## Common fixes

| Problem | Fix |
|---------|-----|
| Window flashes and closes | Use `Start PPAP Dashboard.vbs` |
| `No module named streamlit` | Run the pip install line above |
| No browser opens | Manually open http://localhost:8501 after the terminal says "Starting dashboard" |

## OneDrive inbox path

In the dashboard sidebar, confirm your PPAP Inbox path, then click **Run triage now**.
