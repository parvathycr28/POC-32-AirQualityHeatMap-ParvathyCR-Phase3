Today 12:55 AM
04_INFOCREON_AZURE_CLOUD_DEPLOYMENT (1).docx
Document

Confirm Local Docker Validation
↓
Review the Azure Deployment Guide
↓
Confirm Azure Subscription and Region
↓
Create the Approved Azure Resources
↓
Build and Push Container Image(s)
↓
Deploy Backend Container App
↓
Configure Backend Environment Variables
↓
Validate Backend Endpoint
↓
Deploy Frontend Container App
↓
Configure Frontend-to-Backend URL
↓
Validate the Public Application
↓
Review Logs and Container Health
↓
Restart or Redeploy and Revalidate
↓
Update README and Deployment Notes
↓
Capture Evidence
↓
Submit for Review Deployment Validation Checklist

Application
Pages load correctly
APIs respond correctly
Filters work
Data loads correctly
Visualizations render correctly
Intelligence interactions work
Responsive behaviour is preserved
No unresolved browser-console errors remain
Cloud
Container revision is healthy
Deployment status is successful
Public URL is accessible
Backend endpoint is reachable
Restart or redeployment does not break the application
Logs show no critical failures
Environment variables are configured correctly
Unused resources are removed
Engineering
Phase 2 repository is updated
Final code is committed
Deployment instructions are documented
Environment-variable names are documented
Secrets are not committed
Known limitations are documented
Another developer can understand the deployment flow instead of azure lets use render app for everything mentioned above
deploy failed

Good — we found the accidental change precisely.

The Render documentation was appended to frontend/README.md, and it also contains the literal <<'EOF'. We should clean that up before touching the correct README.

Next step — restore only the accidental frontend change

Run this in Git Bash:

git restore frontend/README.md

Then run:

git status --short

You should get no output.

Send me the result. We will then add the Render section to the root README.md safely.

$ git restore frontend/README.md

ACER@DESKTOP-ISEGCRS UCRT64 ~/Documents/POC-32-AirQualityHeatmap-ParvathyCR1/POC-32-AirQualityHeatmap-ParvathyCR-Phase2(main)
$ git restore frontend/README.md

Good. 👍

Next step

Now run:

git status --short

If it produces no output, the accidental frontend README change is fully removed.

Send me the result.

give me the updated read me file

Here is the updated README with the Render deployment section added and the accidental EOF issue removed.

Download the updated README.md

It includes:

Existing project description and architecture
Backend Render deployment details
Frontend Render deployment details
Environment-variable names
Deployment flow
Live deployment validation results
Local Docker Compose instructions
Secret-handling guidance 
README.md
Document

Library
/
README.md
Aether Pulse — Air Quality Heatmap
Real-Time Air Intelligence Dashboard

Aether Pulse is a production-style demonstration for the Real Rails Intelligence Library, focused on the Data & Intelligence rail.

It combines air-quality observations, population context, spatial visualization, exposure scoring, and city comparison into an interactive intelligence dashboard.

Project
Item	Details
PoC	32
Project	Air Quality Heatmap
Dashboard	Aether Pulse
Rail	Data & Intelligence
Primary Air Quality Source	OpenAQ
Population Source	WorldPop
Frontend	Next.js + TypeScript + Tailwind CSS
Backend	Python FastAPI + Pandas
Map	Leaflet / React Leaflet
Charts	Recharts
Containerization	Docker + Docker Compose
What Aether Pulse Does

Aether Pulse turns air-quality data into understandable intelligence.

Core capabilities
Interactive city air-quality map
Pollutant selection
City search
City comparison
Time-series visualization
Exposure scoring
Population context
Intelligence insights
Live-data status
Fallback-data handling
Downloadable sample data

The dashboard is designed for three audiences:

Everyday viewers — understand what the data means
Builders — understand how the data and application work
Allocators — understand where environmental intelligence and exposure matter
Architecture

The application follows a three-layer architecture.

OpenAQ ───────────────┐
                      │
WorldPop ─────────────┤
                      ▼
               Data Adapters
                      │
                      ▼
              FastAPI Backend
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   Air Quality     Exposure     Comparison
     Service        Scoring       Service
        │             │             │
        └─────────────┼─────────────┘
                      │
                JSON / GeoJSON
                      │
                      ▼
              Next.js Frontend
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
       Map          Charts      Intelligence
                                  Sidebar
Render Deployment

The Phase 2 application is deployed to Render as two Docker-based Web Services.

Services
Service	Purpose	Public URL
poc-32-airqualityheatmap-backend	FastAPI backend	https://poc-32-airqualityheatmap-backend.onrender.com
poc-32-airqualityheatmap-frontend	Next.js frontend	https://poc-32-airqualityheatmap-frontend.onrender.com

Both services use the main branch of the Phase 2 GitHub repository.

Backend Deployment

The backend service uses:

Dockerfile: backend/Dockerfile
Docker build context: repository root
Region: Singapore
Compute plan: Render Free

The backend Docker image installs the Python dependencies and copies:

backend/app
backend/data

The backend listens on port 8001.

Backend environment variables

The following environment variables are configured in Render:

OPENAQ_API_KEY
OPENAQ_BASE_URL
WORLDPOP_BASE_URL
FRONTEND_URL
WORLDPOP_YEAR
WORLDPOP_RESOLUTION

Secret values are configured directly in Render and are not committed to the repository.

FRONTEND_URL must contain the public frontend URL:

https://poc-32-airqualityheatmap-frontend.onrender.com
Frontend Deployment

The frontend service uses:

Dockerfile: frontend/Dockerfile
Docker build context: frontend
Region: Singapore
Compute plan: Render Free

The frontend is built using the public backend URL:

NEXT_PUBLIC_API_URL=https://poc-32-airqualityheatmap-backend.onrender.com
Deployment Flow
Push changes to the main branch.
Render builds the backend Docker service.
Render deploys the backend service.
Render builds the frontend Docker service.
The frontend uses NEXT_PUBLIC_API_URL to communicate with the deployed backend.
The backend allows the deployed frontend origin through FRONTEND_URL.
Validation

The deployed application was validated after deployment:

Backend public URL is reachable.
FastAPI Swagger documentation is accessible.
Air-quality API requests return successful responses.
Frontend public URL is accessible.
Air-quality map loads successfully.
Pollutant/filter interaction works.
Map interaction works.
Population/data interaction works.
Frontend-to-backend CORS communication works.
Browser console contains no unresolved CORS or fetch errors.
Backend logs show successful OpenAQ requests.
Backend service reports as live in Render.
Local Development

For local development, Docker Compose can be used:

docker compose up -d --build

The local services use:

Frontend: http://localhost:3000
Backend: http://localhost:8001

Do not commit .env or other secret files. Use the provided .env.example files as templates for environment-variable names.