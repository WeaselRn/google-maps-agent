# AI Navigation Copilot

Multimodal AI agent for route-aware navigation assistance.
Uses **OpenStreetMap**, **OSRM**, **Overpass API**, and **Google Gemini** (via ADK).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agent | Google ADK + Gemini 2.0 Flash |
| Routing | OSRM (Open Source Routing Machine) |
| Places | Overpass API (OpenStreetMap) |
| Geocoding | Nominatim |
| Map Rendering | MapLibre GL JS + react-map-gl |
| Backend | Python, FastAPI, uvicorn |
| Frontend | React, TypeScript, Vite, Tailwind CSS |

## Project Structure

```
google-agent/
├── backend/
│   ├── agent/        # ADK agent + system prompt
│   ├── api/          # POST /agent endpoint
│   ├── tools/        # Route, places, detour tools
│   ├── main.py       # FastAPI entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/  # MapView, ChatPanel, SearchBar, etc.
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript interfaces
│   └── vite.config.ts
└── README.md
```

## Setup

### Backend

```bash
cd backend
cp .env.example .env   # fill in GEMINI_API_KEY
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-----------|
| `GEMINI_API_KEY` | Google Gemini API key (for ADK agent) |
| `OSRM_BASE_URL` | OSRM server URL (default: `https://router.project-osrm.org`) |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-----------|
| `VITE_API_BASE_URL` | Backend URL (default: `http://localhost:8080`) |

> **Note:** MapLibre uses free OpenStreetMap tiles — no API key needed for map rendering.

## Usage

1. Start the backend on port 8080
2. Start the frontend dev server
3. Open `http://localhost:5173`
4. Try: **"Find cafes along my route from Ernakulam to Fort Kochi"**

## Deployment

### Docker (Backend)

```bash
cd backend
docker build -t navigation-copilot .
docker run -p 8080:8080 --env-file .env navigation-copilot
```

### Frontend Build

```bash
cd frontend
npm run build  # outputs to dist/
```
