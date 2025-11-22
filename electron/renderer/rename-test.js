// Rename function using native Electron dialog
async function renameConversation(conversationId, currentTitle) {
    console.log('✏️ Opening rename dialog for:', conversationId, currentTitle);

    try {
        const newTitle = await window.electronAPI.showRenameDialog(currentTitle);

        if (!newTitle || newTitle === currentTitle) {
            console.log('Rename cancelled');
            return;
        }

        console.log('Sending rename request with new title:', newTitle);
        const response = await fetch(`${API_URL}/conversation/${conversationId}/rename`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newTitle.trim() })
        });
        const data = await response.json();

        if (data.status === 'success') {
            console.log('✅ Rename successful!');
            await loadConversationHistory();
        } else {
            alert('Failed to rename: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('❌ Rename error:', error);
        alert('Error: ' + error.message);
    }
}
