import { API_URL } from './config.js';
import { state } from './state.js';

export async function fetchAvailableModels() {
    try {
        const response = await fetch(`${API_URL}/models/available`);
        if (!response.ok) throw new Error('Failed to fetch models');
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { status: 'error', error: error.message };
    }
}

export async function sendToBackend(message) {
    try {
        const payload = { message, model: state.currentModel };
        if (state.currentConversationId) {
            payload.conversation_id = state.currentConversationId;
        }
        const response = await fetch(`${API_URL}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { status: 'error', error: error.message };
    }
}

export async function startVoice() {
    return await fetch(`${API_URL}/voice/start`, { method: 'POST' });
}

export async function stopVoice() {
    return await fetch(`${API_URL}/voice/stop`, { method: 'POST' });
}

export async function listenVoice() {
    const response = await fetch(`${API_URL}/voice/listen`);
    return await response.json();
}

export async function getTTSStatus() {
    const response = await fetch(`${API_URL}/settings/tts`);
    return await response.json();
}

export async function setTTSStatus(enabled) {
    const response = await fetch(`${API_URL}/settings/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
    });
    return await response.json();
}
