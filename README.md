# GardenProject

GardenProject is an agricultural intelligence application written by OpenAI Codex under human direction. 
It contains:

- FastAPI backend
- Streamlit frontend
- Separate `backend` and `frontend` folders
- A Crop Intelligence Agent that orchestrates weather, drought, yield-history,
  crop-progress, and similar-season services
- Resilient live integrations with clearly labeled demo fallbacks

## Live Development Site

Use the current development deployment at:

**[https://gardenproject-frontend-jekwkhdcya-uc.a.run.app](https://gardenproject-frontend-jekwkhdcya-uc.a.run.app)**

API health check:

**[https://gardenproject-api-jekwkhdcya-uc.a.run.app/health](https://gardenproject-api-jekwkhdcya-uc.a.run.app/health)**

This is an experimental development service. When a configured live integration
is unavailable, the UI marks the result in red and reports that the assessment
defaulted to demo data. Intentionally demo-only services are labeled separately.

## Integration Points

- **NOAA Climate Data Online** - recent daily weather observations used for
  average high and low temperature, precipitation, and extreme-heat counts.
- **U.S. Drought Monitor** - county-level drought severity and Drought Severity
  and Coverage Index context.
- **USDA NASS Quick Stats** - crop-progress estimates, crop availability, and
  historical yield records when an API key and compatible crop/location data are
  available.
- **ZIP/state/county location helpers** - state, county, county FIPS, and ZIP
  context used to route integration requests.
- **Similarity service** - currently returns deterministic demo season matches
  while the vector database integration is planned.

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

## Future Enhancements

- Add production similarity modeling for agricultural seasons.
- Store crop, weather, drought, yield, soil, timing, and location features as
  embeddings in a vector database such as pgvector, ChromaDB, or Pinecone.
- Replace deterministic demo similar-season matches with nearest-neighbor
  retrieval over embedded historical growing-season records.
- Add confidence scoring that separates missing credentials, provider outages,
  unsupported crop/location combinations, and intentionally demo-only services.
- Add path-scoped Cloud Build triggers so frontend and backend deployments run
  only when their source folders change.

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
