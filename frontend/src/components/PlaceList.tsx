/**
 * PlaceList Component
 * Displays a ranked list of place recommendations in the sidebar.
 */

import type { Place } from '../types/mapTypes';
import { Star, Clock, MapPin } from 'lucide-react';

interface PlaceListProps {
    places: Place[];
    selectedPlaceId?: string | null;
    onSelectPlace?: (place: Place) => void;
}

export default function PlaceList({ places, selectedPlaceId, onSelectPlace }: PlaceListProps) {
    if (places.length === 0) {
        return null;
    }

    return (
        <div className="border-t border-slate-700">
            <div className="px-4 py-3">
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Recommendations ({places.length})
                </h3>
            </div>

            <div className="overflow-y-auto max-h-[40vh] space-y-1 px-2 pb-2">
                {places.map((place, index) => (
                    <button
                        key={place.place_id ?? `${place.lat}-${place.lng}`}
                        onClick={() => onSelectPlace?.(place)}
                        className={`place-card w-full text-left p-3 rounded-lg transition-colors ${selectedPlaceId === place.place_id
                            ? 'bg-emerald-500/15 ring-1 ring-emerald-500/30'
                            : 'hover:bg-slate-700/50'
                            }`}
                    >
                        <div className="flex items-start gap-2">
                            {index === 0 && (
                                <Star size={14} className="text-yellow-400 mt-0.5 shrink-0 fill-yellow-400" />
                            )}
                            {index !== 0 && (
                                <MapPin size={14} className="text-slate-500 mt-0.5 shrink-0" />
                            )}
                            <div className="min-w-0 flex-1">
                                <p className="text-sm font-medium text-slate-200 truncate">{place.name}</p>
                                <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
                                    {place.rating != null && (
                                        <span className="flex items-center gap-1">
                                            <Star size={10} className="text-yellow-400 fill-yellow-400" />
                                            {place.rating.toFixed(1)}
                                        </span>
                                    )}
                                    {place.detour_minutes != null && (
                                        <span className="flex items-center gap-1">
                                            <Clock size={10} />
                                            +{place.detour_minutes.toFixed(0)} min detour
                                        </span>
                                    )}
                                </div>
                                {place.address && (
                                    <p className="text-xs text-slate-500 mt-1 truncate">{place.address}</p>
                                )}
                            </div>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}
