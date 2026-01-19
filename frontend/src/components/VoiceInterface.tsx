"use client";

import { useState, useRef } from "react";
import axios from "axios";
import { Mic, Square, Loader2, Volume2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { bufferToWav } from "@/lib/wav-utils";

export default function VoiceInterface() {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [userTranscript, setUserTranscript] = useState("");
    const [agentResponse, setAgentResponse] = useState("");
    const [hasStarted, setHasStarted] = useState(false);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    const handleStart = async () => {
        setIsProcessing(true);
        try {
            const res = await axios.get("http://localhost:8000/greet");
            setAgentResponse(res.data.text);
            const fullAudioUrl = `http://localhost:8000${res.data.audio_url}`;
            setAudioUrl(fullAudioUrl);
            const audio = new Audio(fullAudioUrl);
            await audio.play();
            setHasStarted(true);
        } catch (err) {
            console.error("Failed to initialize greeting:", err);
            // Even if audio fails, let them start so they can click the mic
            setHasStarted(true);
        } finally {
            setIsProcessing(false);
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current);
                const arrayBuffer = await audioBlob.arrayBuffer();
                const audioContext = new AudioContext({ sampleRate: 16000 });
                const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                const wavBlob = bufferToWav(audioBuffer);
                sendAudioToBackend(wavBlob);
                await audioContext.close();
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Error accessing mic:", err);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const sendAudioToBackend = async (audioBlob: Blob) => {
        setIsProcessing(true);
        const formData = new FormData();
        formData.append("audio", audioBlob, "user_voice.wav");

        try {
            const response = await axios.post("http://localhost:8000/voice-chat", formData);
            const { user_text, agent_text, audio_url } = response.data;

            setUserTranscript(user_text);
            setAgentResponse(agent_text);
            const fullUrl = `http://localhost:8000${audio_url}`;
            setAudioUrl(fullUrl);

            const audio = new Audio(fullUrl);
            audio.play();
        } catch (err) {
            console.error("Error sending voice to backend:", err);
        } finally {
            setIsProcessing(false);
        }
    };

    if (!hasStarted) {
        return (
            <div className="flex flex-col items-center justify-center space-y-6 p-12 bg-white/10 backdrop-blur-md rounded-3xl border border-white/20 shadow-2xl">
                <h2 className="text-3xl font-bold text-white mb-2">DriveAI Assistant</h2>
                <p className="text-gray-300 text-center max-w-sm">Tap below to start your personalized dealership consultation.</p>
                <button
                    onClick={handleStart}
                    disabled={isProcessing}
                    className="mt-4 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-semibold shadow-lg transition-all flex items-center space-x-3 disabled:opacity-50"
                >
                    {isProcessing ? (
                        <Loader2 className="w-6 h-6 animate-spin" />
                    ) : (
                        <Volume2 className="w-6 h-6" />
                    )}
                    <span>Start Consultation</span>
                </button>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center space-y-8 p-8 bg-white/10 backdrop-blur-md rounded-3xl border border-white/20 shadow-2xl">
            <h2 className="text-2xl font-bold text-white">DriveAI Assistant</h2>

            <div className="relative">
                <AnimatePresence>
                    {isRecording && (
                        <motion.div
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1.2, opacity: 0.5 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            className="absolute inset-0 bg-red-500 rounded-full blur-xl"
                        />
                    )}
                </AnimatePresence>

                <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isProcessing}
                    className={`relative z-10 p-6 rounded-full transition-all duration-300 ${isRecording ? "bg-red-500 hover:bg-red-600" : "bg-blue-600 hover:bg-blue-700"
                        } text-white shadow-lg disabled:opacity-50`}
                >
                    {isProcessing ? (
                        <Loader2 className="w-8 h-8 animate-spin" />
                    ) : isRecording ? (
                        <Square className="w-8 h-8" />
                    ) : (
                        <Mic className="w-8 h-8" />
                    )}
                </button>
            </div>

            <div className="w-full max-w-md space-y-4">
                {userTranscript && (
                    <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <p className="text-sm text-gray-400">You said:</p>
                        <p className="text-white italic">"{userTranscript}"</p>
                    </div>
                )}

                {agentResponse && (
                    <div className="p-4 bg-blue-500/10 rounded-xl border border-blue-500/20">
                        <p className="text-sm text-blue-400">Agent:</p>
                        <p className="text-white font-medium">{agentResponse}</p>
                        {audioUrl && (
                            <button
                                onClick={() => new Audio(audioUrl).play()}
                                className="mt-2 flex items-center space-x-2 text-xs text-blue-400 hover:text-blue-300"
                            >
                                <Volume2 className="w-4 h-4" />
                                <span>Replay Voice</span>
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
