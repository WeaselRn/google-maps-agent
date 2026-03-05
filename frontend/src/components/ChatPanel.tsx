/**
 * ChatPanel Component
 * Displays conversation history between the user and the AI agent.
 */

import type { ChatMessage } from '../types/mapTypes';
import { Bot, User } from 'lucide-react';

interface ChatPanelProps {
    messages: ChatMessage[];
    isLoading: boolean;
}

export default function ChatPanel({ messages, isLoading }: ChatPanelProps) {
    return (
        <div className="flex flex-col h-full">
            <div className="px-4 py-3 border-b border-slate-700">
                <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <Bot size={16} className="text-emerald-400" />
                    Navigation Assistant
                </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-slate-500 py-8">
                        <Bot size={32} className="mx-auto mb-3 text-emerald-400/50" />
                        <p className="text-sm">Ask me to find places along your route.</p>
                    </div>
                )}

                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`chat-msg flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        {msg.role === 'agent' && (
                            <div className="w-7 h-7 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                                <Bot size={14} className="text-emerald-400" />
                            </div>
                        )}
                        <div
                            className={`max-w-[85%] rounded-xl px-3 py-2 text-sm leading-relaxed ${msg.role === 'user'
                                ? 'bg-blue-600 text-white'
                                : 'bg-slate-700 text-slate-200'
                                }`}
                        >
                            {msg.content}
                        </div>
                        {msg.role === 'user' && (
                            <div className="w-7 h-7 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
                                <User size={14} className="text-blue-400" />
                            </div>
                        )}
                    </div>
                ))}

                {isLoading && (
                    <div className="flex gap-3">
                        <div className="w-7 h-7 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                            <Bot size={14} className="text-emerald-400" />
                        </div>
                        <div className="bg-slate-700 rounded-xl px-4 py-3 text-sm text-slate-400">
                            <span className="animate-pulse">AI analyzing route...</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
