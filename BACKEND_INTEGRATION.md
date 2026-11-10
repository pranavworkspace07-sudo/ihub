# Backend integration contract

The frontend expects a Python API (recommended: FastAPI). Adjust `services/api_client.py` if your backend routes differ.

## Required endpoints

### GET /health
```json
{"status":"ok","service":"electronics-procurement-api"}
```

### POST /api/analysis
Multipart form fields:
- project_id, project_name, required_date, budget_inr, currency, notes
- bom_file (one file)
- quotation_files (repeated files)
- availability_files (repeated files)

Example response:
```json
{"project_id":"PRJ001","analysis_status":"queued","message":"Analysis submitted"}
```
Backend should store uploads, validate BOM, trigger SNS Agent Workbench through its supported API/webhook, and return a job/run identifier.

### GET /api/recommendations/{project_id}
```json
{
 "project_id":"PRJ001",
 "analysis_status":"completed",
 "approval_status":"pending",
 "total_estimated_cost":1650,
 "currency":"INR",
 "recommended_supplier":"SUP001",
 "recommendation":{"primary_supplier":"SUP001","reason":"Best score using validated evidence","risks":["Stock is reported, not reserved."]},
 "supplier_comparison":[{"supplier_id":"SUP001","unit_price":165,"score":91.5}],
 "components":[{"mpn":"ATmega328P","required_quantity":10}]
}
```

### POST /api/approvals
Request:
```json
{"project_id":"PRJ001","decision":"approved","comments":"Reviewed"}
```
Allowed decisions: `approved`, `edit_requested`, `rejected`.

### GET /api/approvals/history?project_id=PRJ001
Response:
```json
{"items":[{"project_id":"PRJ001","decision":"approved","approved_by":"user-123","created_at":"2026-11-10T09:00:00Z"}]}
```

## Architecture
Streamlit → Python API → file validation/storage → SNS Agent Workbench → Python deterministic calculation engine → Supabase → Streamlit.

Keep NVIDIA and Supabase secrets on the backend. The browser/frontend must never receive Supabase service-role keys. Authenticate users and enforce approval permissions server-side. Use HTTPS outside local development.

## Important
SNS Workbench's exact trigger API/webhook depends on your account/version. Implement that integration in the backend, not in Streamlit. Do not treat example responses or sample supplier records as live evidence. Human approval is required before any purchase order or payment.
