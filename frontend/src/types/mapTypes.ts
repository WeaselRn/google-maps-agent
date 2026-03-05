/**
 * TypeScript interfaces for map and agent data.
 */

/** A geographic coordinate */
export interface Coordinate {
    lat: number;
    lng: number;
}

/** A place returned by the agent */
export interface Place {
    name: string;
    lat: number;
    lng: number;
    rating: number | null;
    detour_minutes: number | null;
    place_id?: string;
    address?: string;
}

/** A computed route */
export interface Route {
    path: { lat: number; lng: number }[] | null;
    distance: string | null;
    duration: string | null;
}

/** A proactive stop suggestion */
export interface Suggestion {
    type: string;
    name: string;
    lat: number;
    lng: number;
    detour_minutes: number | null;
}

/** Full response from POST /agent */
export interface AgentResponse {
    summary: string;
    places: Place[];
    route: Route | null;
    suggestions: Suggestion[];
}

/** A single message in the chat history */
export interface ChatMessage {
    id: string;
    role: 'user' | 'agent';
    content: string;
    timestamp: Date;
    places?: Place[];
}
