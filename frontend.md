ANTIGRAVITY FRONTEND GENERATION PROMPT
Google Maps Style AI Navigation Interface

Context:
The backend navigation agent and APIs are already implemented.

Now generate a modern frontend interface that integrates the AI navigation agent with an interactive map.

The UI should resemble the experience of modern navigation apps such as Google Maps.

---

1. FRONTEND STACK

Use:

React
TypeScript
Vite

Libraries:

Google Maps JavaScript API
Axios (for API calls)
Tailwind CSS (for styling)

Optional libraries:

lucide-react for icons
react-speech-recognition or Web Speech API for voice input

---

2. APPLICATION LAYOUT

Create a map-first interface.

Layout structure:

---

## | Search bar + Voice button                    |

| Sidebar AI assistant |       MAP             |
|                      |                       |
| Agent messages      |                       |
| Suggested stops     |                       |
| Route details       |                       |
-----------------------------------------------

Requirements:

The map must occupy the majority of the screen.

The assistant panel should appear as a sidebar.

---

3. CORE COMPONENTS

Create these React components.

MapView.tsx

Responsibilities:
Initialize Google Map
Render markers
Render route polyline
Center map on selected results

---

ChatPanel.tsx

Responsibilities:
Display conversation history
Show agent responses
Display place recommendations

---

SearchBar.tsx

Responsibilities:
Text input
Submit queries to backend

---

VoiceInput.tsx

Responsibilities:
Microphone button
Convert speech to text
Send transcript to backend

---

PlaceList.tsx

Responsibilities:
Show ranked places returned by agent
Display rating and detour time
Clicking a place should highlight it on the map

---

RouteOverlay.tsx

Responsibilities:
Render route returned by backend

---

4. MAP BEHAVIOR

Initialize map using Google Maps JavaScript API.

Map features required:

Display route polyline

Display markers for places returned by agent

Clicking a marker shows an info window with:

place name
rating
detour time

When a user selects a place in the sidebar, the map should:

pan to the location
open marker popup

---

5. AGENT INTERACTION FLOW

User enters a query.

Example:

"Find cafes along my route to Fort Kochi"

Frontend sends POST request to backend:

POST /agent

Body:

{
query: "Find cafes along my route to Fort Kochi"
}

Backend returns structured result:

{
summary: "...",
places: [...],
route: {...}
}

Frontend must:

Display summary in chat panel

Add markers for returned places

Draw route polyline

Populate sidebar list with places

---

6. VOICE INPUT

Add a microphone button in the search bar.

Voice interaction flow:

User clicks microphone

Speech is captured using browser Web Speech API

Speech converted to text

Text sent to backend

The transcript appears in chat history.

---

7. MAP STYLING

Use modern map styling similar to navigation apps.

Enable:

zoom controls
map panning
marker animations

Markers should have hover and click interactions.

---

8. UX DETAILS

Display loading spinner while waiting for agent response.

Show animated message:

"AI analyzing route..."

Animate markers appearing on the map.

Highlight best recommendation visually.

---

9. RESPONSIVE DESIGN

Ensure UI works on:

desktop
tablet
mobile

On mobile:

sidebar becomes collapsible bottom panel.

---

10. PROJECT STRUCTURE

Create frontend directory:

frontend/
src/
components/
MapView.tsx
ChatPanel.tsx
VoiceInput.tsx
SearchBar.tsx
PlaceList.tsx
RouteOverlay.tsx
services/
api.ts
types/
mapTypes.ts
App.tsx
main.tsx

---

11. API SERVICE

Create api.ts to handle backend requests.

Example:

sendQuery(query: string)

Returns agent response containing route and places.

---

12. ENVIRONMENT VARIABLES

Use .env for:

VITE_GOOGLE_MAPS_API_KEY

Do not hardcode API keys.

---

13. INITIAL SCREEN STATE

When the app loads:

Display map centered on a default location.

Example default:

Kochi, India.

Display message in assistant panel:

"Ask me to find places along your route."

---

14. DEMO INTERACTION

Example demo sequence:

User speaks:

"Find cafes along my route to Lulu Mall"

System response:

Agent summary appears in chat panel.

Map draws route.

Cafes appear as markers.

Sidebar lists top 5 results.

---

15. VISUAL POLISH

Use smooth animations.

Markers should appear with fade-in animation.

Sidebar recommendations should animate in.

Highlight the best place with a star icon.

---

End UI generation prompt.
