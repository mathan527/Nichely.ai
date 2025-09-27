/**
 * Professional Loading Component for Nichely App
 * Displays animated logo, progress, and status messages
 */

class LoadingManager {
    constructor() {
        this.loadingElement = null;
        this.progressText = null;
        this.progressFill = null;
        this.isShowing = false;
        this.currentProgress = 0;
        this.messages = [
            "Initializing AI agents...",
            "Analyzing market data...",
            "Processing Reddit discussions...",
            "Generating startup insights...",
            "Preparing detailed analysis...",
            "Finalizing results..."
        ];
        this.currentMessageIndex = 0;
    }

    show() {
        if (this.isShowing) return;
        
        this.isShowing = true;
        this.createLoadingElement();
        this.startProgressAnimation();
        this.startMessageRotation();
    }

    hide() {
        if (!this.isShowing) return;
        
        this.isShowing = false;
        
        if (this.loadingElement) {
            this.loadingElement.classList.add('fade-out');
            setTimeout(() => {
                if (this.loadingElement && this.loadingElement.parentNode) {
                    this.loadingElement.parentNode.removeChild(this.loadingElement);
                }
                this.loadingElement = null;
            }, 500);
        }
    }

    createLoadingElement() {
        // Remove existing loading element if any
        const existing = document.querySelector('.loading-container');
        if (existing) {
            existing.remove();
        }

        // Create loading container
        this.loadingElement = document.createElement('div');
        this.loadingElement.className = 'loading-container';
        this.loadingElement.innerHTML = `
            <img src="/static/src.webp" alt="Nichely Logo" class="loading-logo" onerror="this.style.display='none'">
            <h1 class="loading-title">Nichely</h1>
            <p class="loading-subtitle">AI-Powered Niche Discovery Platform</p>
            
            <div class="loading-spinner"></div>
            
            <div class="loading-progress">
                <div class="loading-progress-text">Initializing AI agents...</div>
                <div class="loading-progress-bar">
                    <div class="loading-progress-fill"></div>
                </div>
                <div class="loading-dots">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
        `;

        // Get references to progress elements
        this.progressText = this.loadingElement.querySelector('.loading-progress-text');
        this.progressFill = this.loadingElement.querySelector('.loading-progress-fill');

        // Add to body
        document.body.appendChild(this.loadingElement);
    }

    startProgressAnimation() {
        if (!this.isShowing) return;

        const duration = 3000; // 3 seconds
        const startTime = Date.now();
        
        const animate = () => {
            if (!this.isShowing) return;

            const elapsed = Date.now() - startTime;
            const progress = Math.min((elapsed / duration) * 100, 95); // Cap at 95% until manually completed
            
            if (this.progressFill) {
                this.progressFill.style.width = `${progress}%`;
            }
            
            this.currentProgress = progress;

            if (progress < 95) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    startMessageRotation() {
        if (!this.isShowing) return;

        const rotateMessages = () => {
            if (!this.isShowing) return;

            if (this.progressText && this.messages[this.currentMessageIndex]) {
                this.progressText.textContent = this.messages[this.currentMessageIndex];
                this.currentMessageIndex = (this.currentMessageIndex + 1) % this.messages.length;
            }

            setTimeout(rotateMessages, 800); // Change message every 800ms
        };

        setTimeout(rotateMessages, 500); // Start after 500ms
    }

    setProgress(percentage, message) {
        if (this.progressFill) {
            this.progressFill.style.width = `${percentage}%`;
        }
        if (message && this.progressText) {
            this.progressText.textContent = message;
        }
    }

    complete() {
        if (this.progressFill) {
            this.progressFill.style.width = '100%';
        }
        if (this.progressText) {
            this.progressText.textContent = 'Analysis complete!';
        }
        
        setTimeout(() => {
            this.hide();
        }, 800);
    }
}

// Global loading manager instance
const loadingManager = new LoadingManager();

// Make loadingManager available globally
window.loadingManager = loadingManager;

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LoadingManager;
}

// Global functions for easy access (keeping these for backward compatibility)
window.showLoading = () => loadingManager.show();
window.hideLoading = () => loadingManager.hide();
window.setLoadingProgress = (percentage, message) => loadingManager.setProgress(percentage, message);
window.completeLoading = () => loadingManager.complete();