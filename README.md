# GardenProject

GardenProject is an agricultural intelligence application built entirely by Codex. It contains:

- FastAPI backend
- Streamlit frontend
- Separate `backend` and `frontend` folders
- A Crop Intelligence Agent that orchestrates weather, drought, yield-history,
  crop-progress, and similar-season services
- Resilient live integrations with clearly labeled demo fallbacks

Optional API credentials:

```text
NOAA_CDO_TOKEN=your_noaa_token
USDA_NASS_API_KEY=your_nass_key
```

Copy `.env.example` to `.env` in the project root and add the credentials.
GardenProject loads that file automatically without overriding environment
variables already supplied by the operating system.

The U.S. Drought Monitor integration does not require a key. Retired employee
portal pages are preserved under `frontend/archive/pages` and are not routed.

## Run

```powershell
cd C:\Users\sarah\Source\Repos\GardenProject
.\start.ps1 -Install
```

After dependencies are installed, use:

```powershell
.\start.ps1
```

Frontend: `http://localhost:8501`

API: `http://127.0.0.1:8000`

Stop both local services with:

```powershell
.\stop.ps1
```
