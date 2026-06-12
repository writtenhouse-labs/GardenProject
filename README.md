# GardenProject

Garden Project employee portal scaffold built with the same stack shape as PelagicSeer:

- FastAPI backend
- Streamlit frontend
- Separate `backend` and `frontend` folders
- Employee portal visual language copied from `C:\xampp\htdocs\employee-portal`

The database layer is intentionally stubbed. Endpoints and service functions exist so real persistence can be added later without changing the page structure.

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
