/**
 * MapView Component
 * Renders interactive Google Map with markers, info windows, and route polyline.
 * Uses @react-google-maps/api per refactor.md guidance.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import {
    GoogleMap,
    LoadScript,
    Marker,
    Polyline,
    InfoWindow,
} from '@react-google-maps/api';
import { Star, Clock } from 'lucide-react';
import type { Place, Route } from '../types/mapTypes';

interface MapViewProps {
    places: Place[];
    route: Route | null;
    selectedPlaceId?: string | null;
    onMarkerClick?: (place: Place) => void;
}

// Default center: Kochi, India
const DEFAULT_CENTER = { lat: 9.9312, lng: 76.2673 };
const DEFAULT_ZOOM = 12;

const containerStyle = {
    width: '100%',
    height: '100%',
};

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

export default function MapView({ places, route, selectedPlaceId, onMarkerClick }: MapViewProps) {
    const mapRef = useRef<google.maps.Map | null>(null);
    const [activeMarker, setActiveMarker] = useState<string | null>(null);

    const onMapLoad = useCallback((map: google.maps.Map) => {
        mapRef.current = map;
    }, []);

    // Fit map to route bounds when route changes
    useEffect(() => {
        const map = mapRef.current;
        if (!map || !route?.path?.length) return;

        const bounds = new google.maps.LatLngBounds();
        route.path.forEach((coord) => bounds.extend(coord));
        map.fitBounds(bounds, 60);
    }, [route]);

    // Pan to selected place
    useEffect(() => {
        const map = mapRef.current;
        if (!map || !selectedPlaceId) return;
        const place = places.find((p) => p.place_id === selectedPlaceId);
        if (place) {
            map.panTo({ lat: place.lat, lng: place.lng });
            map.setZoom(15);
            setActiveMarker(selectedPlaceId);
        }
    }, [selectedPlaceId, places]);

    const handleMarkerClick = useCallback(
        (place: Place) => {
            setActiveMarker(place.place_id ?? null);
            onMarkerClick?.(place);
        },
        [onMarkerClick],
    );

    const activePlace = activeMarker
        ? places.find((p) => p.place_id === activeMarker)
        : null;

    return (
        <LoadScript googleMapsApiKey={GOOGLE_MAPS_API_KEY}>
            <GoogleMap
                mapContainerStyle={containerStyle}
                center={DEFAULT_CENTER}
                zoom={DEFAULT_ZOOM}
                onLoad={onMapLoad}
                options={{
                    disableDefaultUI: false,
                    zoomControl: true,
                    mapTypeControl: false,
                    streetViewControl: false,
                    fullscreenControl: false,
                    styles: [
                        { elementType: 'geometry', stylers: [{ color: '#1d2c4d' }] },
                        { elementType: 'labels.text.fill', stylers: [{ color: '#8ec3b9' }] },
                        { elementType: 'labels.text.stroke', stylers: [{ color: '#1a3646' }] },
                        { featureType: 'water', elementType: 'geometry.fill', stylers: [{ color: '#17263c' }] },
                        { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#304a7d' }] },
                        { featureType: 'road', elementType: 'geometry.stroke', stylers: [{ color: '#255763' }] },
                    ],
                }}
            >
                {/* Route polyline */}
                {route?.path && (
                    <Polyline
                        path={route.path}
                        options={{
                            strokeColor: '#4285F4',
                            strokeOpacity: 0.8,
                            strokeWeight: 4,
                        }}
                    />
                )}

                {/* Place markers with DROP animation */}
                {places.map((place, index) => (
                    <Marker
                        key={place.place_id ?? `${place.lat}-${place.lng}`}
                        position={{ lat: place.lat, lng: place.lng }}
                        title={place.name}
                        animation={google.maps.Animation.DROP}
                        icon={
                            index === 0
                                ? {
                                    url: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                                }
                                : {
                                    url: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                                }
                        }
                        onClick={() => handleMarkerClick(place)}
                    />
                ))}

                {/* Info window popup */}
                {activePlace && (
                    <InfoWindow
                        position={{ lat: activePlace.lat, lng: activePlace.lng }}
                        onCloseClick={() => setActiveMarker(null)}
                    >
                        <div className="p-1 min-w-[160px]">
                            <h3 className="font-semibold text-sm text-gray-900">{activePlace.name}</h3>
                            <div className="flex items-center gap-3 mt-1 text-xs text-gray-600">
                                {activePlace.rating != null && (
                                    <span className="flex items-center gap-1">
                                        <Star size={10} className="text-yellow-500 fill-yellow-500" />
                                        {activePlace.rating.toFixed(1)}
                                    </span>
                                )}
                                {activePlace.detour_minutes != null && (
                                    <span className="flex items-center gap-1">
                                        <Clock size={10} />
                                        +{activePlace.detour_minutes.toFixed(0)} min
                                    </span>
                                )}
                            </div>
                            {activePlace.address && (
                                <p className="text-xs text-gray-500 mt-1">{activePlace.address}</p>
                            )}
                        </div>
                    </InfoWindow>
                )}
            </GoogleMap>
        </LoadScript>
    );
}
