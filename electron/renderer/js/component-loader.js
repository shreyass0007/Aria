/**
 * Loads an HTML component into a target element.
 * @param {string} componentPath - Path to the HTML component file.
 * @param {string} placeholderId - ID of the placeholder element to replace.
 */
export async function loadComponent(componentPath, placeholderId) {
    try {
        const response = await fetch(componentPath);
        if (!response.ok) throw new Error(`Failed to load component: ${componentPath}`);
        const html = await response.text();
        const placeholder = document.getElementById(placeholderId);
        if (placeholder) {
            placeholder.outerHTML = html;
        } else {
            console.error(`Placeholder element not found: ${placeholderId}`);
        }
    } catch (error) {
        console.error(error);
    }
}

/**
 * Loads all core components for the application.
 */
export async function loadAllComponents() {
    await Promise.all([
        loadComponent('components/header.html', 'header-placeholder'),
        loadComponent('components/chat-area.html', 'chat-placeholder'),
        loadComponent('components/input-area.html', 'input-placeholder'),
        loadComponent('components/settings-modal.html', 'settings-modal-placeholder'),
        loadComponent('components/history-sidebar.html', 'history-sidebar-placeholder'),
        loadComponent('components/history-modals.html', 'history-modals-placeholder'),
        loadComponent('components/music-player.html', 'music-player-placeholder')
    ]);
}
