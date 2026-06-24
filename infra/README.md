# Infrastructure

Deploy GardenProject to Cloud Run with:

```powershell
cd C:\Users\sarah\Source\Repos\GardenProject
.\infra\deploy.ps1
```

The script deploys two services to the `gardenproject-dev` project:

- `gardenproject-api`
- `gardenproject-frontend`

Optional production credentials can be added to the Cloud Run API service:

```text
NOAA_CDO_TOKEN
USDA_NASS_API_KEY
```
