/**
 * SearchBar Component
 * Text input with submit button for sending navigation queries.
 */

import { useState } from 'react';
import { Search } from 'lucide-react';
import VoiceInput from './VoiceInput';

interface SearchBarProps {
    onSubmit: (query: string) => void;
    isLoading: boolean;
}

export default function SearchBar({ onSubmit, isLoading }: SearchBarProps) {
    const [query, setQuery] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const trimmed = query.trim();
        if (!trimmed || isLoading) return;
        onSubmit(trimmed);
        setQuery('');
    };

    const handleVoiceResult = (transcript: string) => {
        setQuery(transcript);
        onSubmit(transcript);
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="flex items-center gap-2 px-4 py-3 bg-slate-800 border-b border-slate-700"
        >
            <div className="relative flex-1">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                    id="search-input"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Find cafes along my route to Lulu Mall..."
                    disabled={isLoading}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-700 text-slate-200 placeholder-slate-500 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 disabled:opacity-50"
                />
            </div>
            <VoiceInput onResult={handleVoiceResult} />
            <button
                id="search-submit"
                type="submit"
                disabled={isLoading || !query.trim()}
                className="px-4 py-2.5 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                Search
            </button>
        </form>
    );
}
