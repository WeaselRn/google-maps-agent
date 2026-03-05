/**
 * API Service
 * Handles communication with the backend agent endpoint.
 */

import axios from 'axios';
import type { AgentResponse } from '../types/mapTypes';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Send a natural-language navigation query to the backend agent.
 * @param query — e.g. "Find cafes along my route to Lulu Mall"
 * @returns Structured agent response with summary, places, route, suggestions
 */
export async function sendQuery(query: string): Promise<AgentResponse> {
    const response = await apiClient.post<AgentResponse>('/agent', { query });
    return response.data;
}
