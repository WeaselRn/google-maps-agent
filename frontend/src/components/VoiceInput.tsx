/**
 * VoiceInput Component
 * Microphone button for speech-to-text input using Web Speech API.
 */

import { useState, useRef, useCallback } from 'react';
import { Mic, MicOff } from 'lucide-react';

interface VoiceInputProps {
    onResult: (transcript: string) => void;
}

/* eslint-disable @typescript-eslint/no-explicit-any */
// Web Speech API types are not included in standard DOM typings.
// We use `any` for the recognition instance and event.

export default function VoiceInput({ onResult }: VoiceInputProps) {
    const [isListening, setIsListening] = useState(false);
    const recognitionRef = useRef<any>(null);

    const toggleListening = useCallback(() => {
        const win = window as any;
        const SpeechRecognitionClass = win.SpeechRecognition || win.webkitSpeechRecognition;

        if (!SpeechRecognitionClass) {
            alert('Speech recognition is not supported in this browser.');
            return;
        }

        if (isListening && recognitionRef.current) {
            recognitionRef.current.stop();
            setIsListening(false);
            return;
        }

        const recognition = new SpeechRecognitionClass();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = (event: any) => {
            const transcript: string = event.results[0][0].transcript;
            onResult(transcript);
            setIsListening(false);
        };

        recognition.onerror = () => {
            setIsListening(false);
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        recognitionRef.current = recognition;
        recognition.start();
        setIsListening(true);
    }, [isListening, onResult]);

    return (
        <button
            id="voice-input-btn"
            type="button"
            onClick={toggleListening}
            className={`p-2.5 rounded-lg transition-all ${isListening
                    ? 'bg-red-500/20 text-red-400 ring-2 ring-red-500/50 animate-pulse'
                    : 'bg-slate-700 text-slate-400 hover:text-slate-200 hover:bg-slate-600'
                }`}
            title={isListening ? 'Stop listening' : 'Start voice input'}
        >
            {isListening ? <MicOff size={16} /> : <Mic size={16} />}
        </button>
    );
}
