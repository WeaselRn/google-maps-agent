# AI Navigation Copilot

Multimodal **AI navigation assistant** that helps users discover places along a route using natural language.

The system combines **Google Gemini AI**, **Google Maps APIs**, and a **React map interface** to provide route-aware recommendations such as cafes, restaurants, and fuel stops during a journey.

This project is built for a **Google AI Hackathon** and demonstrates an **agent-based navigation assistant** powered by **Google ADK**.

---

# Architecture Overview

User Query
↓
Gemini Agent (Google ADK)
↓
Google Directions API
↓
Route Sampling Algorithm
↓
Google Places API
↓
Map UI (Google Maps JS API)

---

# Tech Stack

| Layer            | Technology                    |
| ---------------- | ----------------------------- |
| AI Agent         | Google ADK + Gemini 1.5 Flash |
| Routing          | Google Directions API         |
| Places Discovery | Google Places API             |
| Map Rendering    | Google Maps JavaScript API    |
| Backend          | Python, FastAPI, uvicorn      |
| Frontend         | React, TypeScript, Vite       |
| Deployment       | Google Cloud Run              |

---

# Core Features

### Route-Aware Place Discovery

Users can ask questions like:

Find cafes along my route to Fort Kochi.

The system:

1. Calculates the route
2. Samples coordinates along the route
3. Searches nearby places
4. Returns ranked recommendations

---

### AI Navigation Assistant

The AI agent can interpret natural language queries such as:

* Find restaurants along my route
* Add a fuel stop before my destination
* Find vegetarian cafes within 5 minutes detour

The agent decides which tools to call to retrieve route and place information.

---

### Interactive Map Interface

The frontend map displays:

* route overlays
* recommended stops
* clickable place markers

---

# Project Structure

```
google-agent/
├── backend/
│   ├── agent/        # ADK agent configuration + prompts
│   ├── tools/        # Route, places, detour tools
│   ├── api/          # POST /agent endpoint
│   ├── main.py       # FastAPI entry point
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/   # MapView, ChatPanel, SearchBar
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript interfaces
│   └── vite.config.ts
│
└── README.md
```

---

# Setup

## Backend

```
cd backend
cp .env.example .env
```

Add your API keys.

```
pip install -r requirements.txt
python main.py
```

Backend runs at:

```
http://localhost:8080
```

---

## Frontend

```
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open:

```
http://localhost:5173
```

---

# Environment Variables

## Backend (`backend/.env`)

| Variable            | Description                      |
| ------------------- | -------------------------------- |
| GEMINI_API_KEY      | Google Gemini API key            |
| GOOGLE_MAPS_API_KEY | Key for Places + Directions APIs |

---

## Frontend (`frontend/.env`)

| Variable                 | Description            |
| ------------------------ | ---------------------- |
| VITE_GOOGLE_MAPS_API_KEY | Google Maps JS API key |
| VITE_API_BASE_URL        | Backend URL            |

Default backend URL:

```
http://localhost:8080
```

---

# Example Query

```
Find cafes along my route from Ernakulam to Fort Kochi
```

The AI agent will:

1. Compute the route
2. Sample points along the journey
3. Query nearby cafes
4. Return recommendations

The map UI then displays the results as markers.

---

# Deployment

## Backend Deployment (Google Cloud Run)

Build the container:

```
cd backend
docker build -t navigation-copilot .
```

Deploy to Cloud Run.

The backend container runs on port:

```
8080
```

---

## Frontend Build

```
cd frontend
npm run build
```

Production files will be generated in:

```
dist/
```

---

# Future Improvements

* Voice interaction with Gemini Live API
* Traffic-aware route planning
* Contextual stop suggestions during long trips
* Personalized travel recommendations
* Mobile-friendly UI

---

# License

MIT License
