Below is a minimal React component (~40 lines) that will give you a working map UI + markers + route drawing using the Google Maps JavaScript API.

This is perfect for your hackathon because it’s simple but looks like a real navigation product.

1️⃣ Install the Maps React Wrapper

Use the official lightweight wrapper:

npm install @react-google-maps/api
2️⃣ Minimal Map Component

Create:

src/components/MapView.tsx
import { GoogleMap, LoadScript, Marker, Polyline } from "@react-google-maps/api";
import { useState } from "react";

const containerStyle = {
  width: "100%",
  height: "100vh"
};

const center = {
  lat: 9.9312,
  lng: 76.2673 // Kochi default
};

export default function MapView({ places, route }) {
  return (
    <LoadScript googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}>
      <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={12}>

        {/* Render markers */}
        {places?.map((place, i) => (
          <Marker
            key={i}
            position={{ lat: place.lat, lng: place.lng }}
            title={place.name}
          />
        ))}

        {/* Render route */}
        {route && (
          <Polyline
            path={route}
            options={{
              strokeColor: "#4285F4",
              strokeOpacity: 0.8,
              strokeWeight: 4
            }}
          />
        )}

      </GoogleMap>
    </LoadScript>
  );
}
3️⃣ Example Data Format From Backend

Your backend agent should return something like:

{
  "places": [
    {
      "name": "Cafe Papaya",
      "lat": 9.931,
      "lng": 76.267
    },
    {
      "name": "French Toast",
      "lat": 9.945,
      "lng": 76.280
    }
  ],
  "route": [
    { "lat": 9.931, "lng": 76.267 },
    { "lat": 9.945, "lng": 76.280 }
  ]
}

Markers will appear automatically.

4️⃣ Connect It To Your Agent

Example API call:

const askAgent = async (query) => {
  const res = await fetch("http://localhost:8080/agent", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });

  const data = await res.json();
  setPlaces(data.places);
  setRoute(data.route);
};
5️⃣ Environment Variable

Add:

frontend/.env
VITE_GOOGLE_MAPS_API_KEY=your_maps_key

Restart frontend after adding.

6️⃣ Result

When the user says:

Find cafes along my route to Fort Kochi

The UI will:

1️⃣ Draw the route
2️⃣ Add markers for cafes
3️⃣ Let the user click markers

Which looks very close to Google Maps navigation.

7️⃣ Optional (Very Nice Demo Upgrade)

Add animated markers so results appear smoothly:

animation: google.maps.Animation.DROP

Judges love small polish like this.