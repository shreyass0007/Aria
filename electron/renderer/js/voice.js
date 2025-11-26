import { state } from './state.js';
import { startVoice, stopVoice, listenVoice, sendToBackend } from './api.js';
import { addMessage, showThinkingIndicator, removeThinkingIndicator } from './chat.js';

export async function handleToggleVoice() {
    const voiceBtn = document.getElementById('voiceBtn');
    state.voiceModeActive = !state.voiceModeActive;

    if (state.voiceModeActive) {
        voiceBtn.classList.add('active');
        addMessage('🎙️ Voice mode active - Say "Aria" to start', 'aria');

        try {
            await startVoice();
            listenForVoiceInput();
        } catch (error) {
            console.error('Voice mode error:', error);
            state.voiceModeActive = false;
            voiceBtn.classList.remove('active');
        }
    } else {
        voiceBtn.classList.remove('active');
        addMessage('Voice mode deactivated', 'aria');
        stopVoice();
    }
}

async function listenForVoiceInput() {
    if (!state.voiceModeActive) return;

    try {
        const data = await listenVoice();

        if (data.text) {
            addMessage(data.text, 'user');
            showThinkingIndicator();
            const response = await sendToBackend(data.text);
            removeThinkingIndicator();
            if (response.response) {
                addMessage(response.response, 'aria', response.ui_action);
            }
        }

        if (state.voiceModeActive) {
            setTimeout(() => listenForVoiceInput(), 1000);
        }
    } catch (error) {
        console.error('Error listening for voice:', error);
        if (state.voiceModeActive) {
            setTimeout(() => listenForVoiceInput(), 2000);
        }
    }
}
