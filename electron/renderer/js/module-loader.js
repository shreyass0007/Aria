/**
 * Module Loader - Safe loading of optional UI modules
 * Provides error boundaries and graceful degradation
 */

import { FeatureConfig } from './feature-config.js';

export class ModuleLoader {
    constructor() {
        this.loadedModules = new Map();
        this.failedModules = new Set();
        this.loadingModules = new Set();
    }

    /**
     * Load a module safely with error boundary
     * @param {string} moduleName - Name of the module to load
     * @param {Function} initFunction - Async initialization function
     * @param {Object} options - Loading options
     */
    async loadModule(moduleName, initFunction, options = {}) {
        const {
            retryOnError = false,
            showErrorToUser = true,
            fallbackUI = null
        } = options;

        // Check if already loaded
        if (this.loadedModules.has(moduleName)) {
            console.log(`Module ${moduleName} already loaded`);
            return { success: true, cached: true };
        }

        // Check if previously failed
        if (this.failedModules.has(moduleName) && !retryOnError) {
            console.warn(`Module ${moduleName} previously failed, skipping`);
            return { success: false, reason: 'previous_failure' };
        }

        // Check if currently loading
        if (this.loadingModules.has(moduleName)) {
            console.log(`Module ${moduleName} is currently loading`);
            return { success: false, reason: 'already_loading' };
        }

        // Check if feature is enabled
        if (!FeatureConfig.isEnabled(moduleName)) {
            console.log(`Module ${moduleName} is disabled in config`);
            return { success: false, reason: 'disabled' };
        }

        this.loadingModules.add(moduleName);

        try {
            console.log(`Loading module: ${moduleName}...`);

            // Check backend availability if required
            const feature = FeatureConfig.features[moduleName];
            if (feature && feature.requiresBackend) {
                const backendAvailable = await this.checkBackendAvailability(moduleName);
                if (!backendAvailable) {
                    throw new Error(`Backend not available for ${moduleName}`);
                }
            }

            // Execute initialization function
            const result = await initFunction();

            // Mark as loaded
            this.loadedModules.set(moduleName, {
                loadedAt: new Date(),
                result: result
            });

            this.loadingModules.delete(moduleName);
            console.log(`✓ Module ${moduleName} loaded successfully`);

            return { success: true, result };

        } catch (error) {
            console.error(`✗ Failed to load module ${moduleName}:`, error);

            this.failedModules.add(moduleName);
            this.loadingModules.delete(moduleName);

            // Show fallback UI if provided
            if (fallbackUI) {
                this.showFallbackUI(moduleName, fallbackUI, error);
            }

            // Notify user if requested
            if (showErrorToUser) {
                this.notifyUserOfError(moduleName, error);
            }

            return {
                success: false,
                error: error.message,
                reason: 'load_error'
            };
        }
    }

    /**
     * Check if backend is available for a module
     */
    async checkBackendAvailability(moduleName) {
        const feature = FeatureConfig.features[moduleName];
        if (!feature || !feature.backendEndpoint) {
            return true; // No backend check required
        }

        try {
            const response = await fetch(`http://localhost:5000${feature.backendEndpoint}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                return false;
            }

            const data = await response.json();
            return data.available === true || data.status === 'success';

        } catch (error) {
            console.warn(`Backend check failed for ${moduleName}:`, error);
            return false;
        }
    }

    /**
     * Show fallback UI when module fails to load
     */
    showFallbackUI(moduleName, fallbackUI, error) {
        try {
            if (typeof fallbackUI === 'function') {
                fallbackUI(error);
            } else if (typeof fallbackUI === 'string') {
                // Insert fallback HTML
                const container = document.getElementById(`${moduleName}-container`);
                if (container) {
                    container.innerHTML = fallbackUI;
                }
            }
        } catch (err) {
            console.error(`Failed to show fallback UI for ${moduleName}:`, err);
        }
    }

    /**
     * Notify user of module loading error
     */
    notifyUserOfError(moduleName, error) {
        const feature = FeatureConfig.features[moduleName];
        const featureName = feature ? feature.name : moduleName;

        console.warn(`⚠️ ${featureName} is currently unavailable`);

        // Don't show intrusive errors - just log to console
        // User can check console if interested
    }

    /**
     * Load multiple modules in parallel
     */
    async loadModules(moduleDefinitions) {
        const promises = moduleDefinitions.map(({ name, init, options }) =>
            this.loadModule(name, init, options)
        );

        const results = await Promise.allSettled(promises);

        const summary = {
            total: results.length,
            loaded: results.filter(r => r.status === 'fulfilled' && r.value.success).length,
            failed: results.filter(r => r.status === 'rejected' || !r.value.success).length
        };

        console.log(`Module loading summary:`, summary);
        return summary;
    }

    /**
     * Unload a module
     */
    unloadModule(moduleName) {
        if (this.loadedModules.has(moduleName)) {
            this.loadedModules.delete(moduleName);
            console.log(`Module ${moduleName} unloaded`);
            return true;
        }
        return false;
    }

    /**
     * Reload a module
     */
    async reloadModule(moduleName, initFunction, options = {}) {
        this.unloadModule(moduleName);
        this.failedModules.delete(moduleName);
        return await this.loadModule(moduleName, initFunction, options);
    }

    /**
     * Get status of all modules
     */
    getModuleStatus() {
        const status = {};
        Object.keys(FeatureConfig.features).forEach(name => {
            status[name] = {
                enabled: FeatureConfig.isEnabled(name),
                loaded: this.loadedModules.has(name),
                failed: this.failedModules.has(name),
                loading: this.loadingModules.has(name)
            };
        });
        return status;
    }

    /**
     * Check if a module is loaded
     */
    isLoaded(moduleName) {
        return this.loadedModules.has(moduleName);
    }

    /**
     * Check if a module failed
     */
    hasFailed(moduleName) {
        return this.failedModules.has(moduleName);
    }
}

// Export singleton instance
export const moduleLoader = new ModuleLoader();
