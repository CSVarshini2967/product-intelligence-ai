# UniHack Product Intelligence Engine

## Structure
- `backend/` — FastAPI app, 9-module pipeline (see `app/modules/`)
- `frontend/` — Next.js upload UI

## Run it

### Backend
```
cd backend
pip install -r requirements.txt
cp .env.example .env   # then paste your real GEMINI_API_KEY into .env
export $(cat .env | xargs)   # or use python-dotenv
uvicorn app.main:app --reload --port 8000
```

### Frontend
```
cd frontend
npm install
npm run dev
```
Then open http://localhost:3000, upload `backend/data/raw/appliances_scope.csv`
(pre-filtered to the 84 Appliance rows), and click "Run enrichment pipeline."

## Pipeline modules (backend/app/modules/)
1. ingestion — reads CSV, strips placeholder brand values
2. cleaning — deterministic UOM/abbreviation normalization
3. classification — keyword-routed classpath (scoped to Appliances)
4. extraction — the ONLY AI call (Gemini), evidence-linked JSON schema
5. enrichment — stub, pluggable, deliberately not built out (see docstring)
6. validation — checks evidence presence + manufacturer/brand mismatch
7. confidence — scores derived from real signals, not LLM self-rating
8. generation — template-based descriptions from validated fields only
9. export — flattens back to a CSV matching the real Delivery Format shape

## What's already verified working
- Full 9-module pipeline runs end-to-end with zero crashes (see smoke_test.py)
- Classification correctly routes all sample dishwasher rows
- Confidence engine correctly flags rows needing review when extraction has no API key
- Frontend type-checks clean and calls the backend API correctly

## What YOU need to do next
1. Get a Gemini API key: https://aistudio.google.com/apikey
2. Add it to backend/.env
3. Re-run smoke_test.py — you should see real extracted attributes with evidence
4. Build the eval script comparing output against data/reference/Unihack__Expected_Output_-_Delivery_Format.csv
5. Build the dashboard view (Module 10) in the frontend — currently just shows summary stats
