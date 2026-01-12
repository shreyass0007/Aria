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

export async function sendToBackend(message, extraData = null) {
    try {
        const payload = { message, model: state.currentModel };
        if (state.currentConversationId) {
            payload.conversation_id = state.currentConversationId;
        }
        if (extraData) {
            payload.extra_data = extraData;
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

// Feature status endpoints for modular system
export async function checkFeatureStatus(featureName) {
    try {
        const response = await fetch(`${API_URL}/features/${featureName}/status`);
        if (!response.ok) return { available: false };
        return await response.json();
    } catch (error) {
        console.warn(`Feature ${featureName} check failed:`, error);
        return { available: false };
    }
}

export async function checkAllFeaturesStatus() {
    try {
        const response = await fetch(`${API_URL}/features/status`);
        if (!response.ok) throw new Error('Failed to fetch feature status');
        return await response.json();
    } catch (error) {
        console.error('Failed to check features:', error);
        return { status: 'error', features: {} };
    }
}

export async function waitForBackend(maxRetries = 20, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(`${API_URL}/health`);
            if (response.ok) {
                console.log('Backend is ready!');
                return true;
            }
        } catch (error) {
            console.log(`Waiting for backend... (${i + 1}/${maxRetries})`);
        }
        await new Promise(resolve => setTimeout(resolve, delay));
    }
    console.error('Backend failed to start within timeout.');
    return false;
}

// WebSocket Connection
export function connectWebSocket(onMessage) {
    // Convert http(s) to ws(s)
    const wsUrl = API_URL.replace('http', 'ws') + '/ws';
    console.log('Connecting to WebSocket:', wsUrl);

    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log('WebSocket Connected');
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onMessage(data);
        } catch (e) {
            console.error('Error parsing WebSocket message:', e);
        }
    };

    socket.onerror = (error) => {
        console.error('WebSocket Error:', error);
    };

    socket.onclose = () => {
        console.log('WebSocket Closed');
        // Simple reconnect logic could go here
    };

    return socket;
}
