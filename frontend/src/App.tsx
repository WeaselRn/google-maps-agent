/**
 * App — Root layout component
 * Map-first interface with sidebar assistant panel.
 * Responsive: sidebar on desktop, collapsible bottom panel on mobile.
 */

import { useState } from 'react';
import { ChevronUp, ChevronDown, Navigation } from 'lucide-react';

import SearchBar from './components/SearchBar';
import ChatPanel from './components/ChatPanel';
import MapView from './components/MapView';
import PlaceList from './components/PlaceList';

import type { Place, Route, ChatMessage } from './types/mapTypes';
import { sendQuery } from './services/api';

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [places, setPlaces] = useState<Place[]>([]);
  const [route, setRoute] = useState<Route | null>(null);
  const [selectedPlaceId, setSelectedPlaceId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleQuery = async (query: string) => {
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const result = await sendQuery(query);
      setPlaces(result.places);
      setRoute(result.route);

      const agentMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'agent',
        content: result.summary,
        timestamp: new Date(),
        places: result.places,
      };
      setMessages((prev) => [...prev, agentMsg]);
      // Auto-open sidebar on mobile when results arrive
      setSidebarOpen(true);
    } catch (_err) {
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'agent',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPlace = (place: Place) => {
    setSelectedPlaceId(place.place_id ?? null);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-slate-900 text-slate-100 overflow-hidden">
      {/* Top search bar */}
      <SearchBar onSubmit={handleQuery} isLoading={isLoading} />

      {/* Main content: sidebar + map */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Desktop sidebar */}
        <aside className="hidden md:flex w-80 flex-shrink-0 flex-col bg-slate-800 border-r border-slate-700 overflow-hidden">
          <div className="flex-1 overflow-y-auto">
            <ChatPanel messages={messages} isLoading={isLoading} />
          </div>
          {/* Route details */}
          {route && route.path && (
            <div className="border-t border-slate-700 px-4 py-3 bg-slate-800/80">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Navigation size={12} className="text-emerald-400" />
                <span className="font-medium text-slate-200">{route.distance}</span>
                <span className="text-slate-500">·</span>
                <span className="font-medium text-slate-200">{route.duration}</span>
              </div>
            </div>
          )}
          <PlaceList
            places={places}
            selectedPlaceId={selectedPlaceId}
            onSelectPlace={handleSelectPlace}
          />
        </aside>

        {/* Map area */}
        <main className="flex-1 relative">
          <MapView
            places={places}
            route={route}
            selectedPlaceId={selectedPlaceId}
            onMarkerClick={handleSelectPlace}
          />
        </main>

        {/* Mobile bottom sheet */}
        <div
          className={`md:hidden absolute bottom-0 left-0 right-0 bg-slate-800 border-t border-slate-700 transition-transform duration-300 ease-in-out z-20 ${sidebarOpen ? 'translate-y-0' : 'translate-y-[calc(100%-3rem)]'
            }`}
          style={{ maxHeight: '60vh' }}
        >
          {/* Pull tab */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full flex items-center justify-center py-2 text-slate-400 hover:text-slate-200 transition-colors"
          >
            {sidebarOpen ? <ChevronDown size={20} /> : <ChevronUp size={20} />}
            <span className="text-xs ml-1">
              {sidebarOpen ? 'Hide' : messages.length > 0 ? `${messages.length} messages` : 'Assistant'}
            </span>
          </button>

          <div className="overflow-y-auto" style={{ maxHeight: 'calc(60vh - 3rem)' }}>
            {/* Route summary on mobile */}
            {route && route.path && (
              <div className="border-b border-slate-700 px-4 py-2 bg-slate-800/80">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Navigation size={12} className="text-emerald-400" />
                  <span className="font-medium text-slate-200">{route.distance}</span>
                  <span className="text-slate-500">·</span>
                  <span className="font-medium text-slate-200">{route.duration}</span>
                </div>
              </div>
            )}
            <ChatPanel messages={messages} isLoading={isLoading} />
            <PlaceList
              places={places}
              selectedPlaceId={selectedPlaceId}
              onSelectPlace={(place) => {
                handleSelectPlace(place);
                setSidebarOpen(false);
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
