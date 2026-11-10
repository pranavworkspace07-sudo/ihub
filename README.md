# ProcureAI Streamlit Frontend

## Features
- Dashboard
- BOM upload (CSV/XLSX)
- Supplier quotation and stock evidence upload
- Start agent analysis through Python backend
- Supplier comparison and recommendation
- Human approval, change request and rejection
- Approval history and backend health check

## Windows setup
```powershell
py -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
```
Edit `.env` and set `BACKEND_BASE_URL`, then run:
```powershell
streamlit run app.py
```
Open the local URL printed by Streamlit, normally http://localhost:8501.

This is the frontend. It does not include the Python backend, SNS workflow, NVIDIA credentials or Supabase database.
"# ihub" 
