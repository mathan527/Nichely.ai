/**
 * Nichely Intro Page Manager
 * Handles logo zoom animation and smooth transition to search page
 */

class IntroManager {
    constructor() {
        this.introElement = null;
        this.hasIntroPlayed = false;
        this.introDuration = 4200; // Total intro duration in milliseconds
        this.skipTimeout = null;
        this.preloadImages();
    }

    preloadImages() {
        // Preload logo to prevent loading delays
        const img = new Image();
        img.src = '/static/src.webp';
        console.log('🖼️ Preloading logo...');
    }

    init() {
        // Check if intro should be shown (only on first visit or refresh)
        const hasSeenIntro = sessionStorage.getItem('nichely_intro_seen');
        
        if (!hasSeenIntro) {
            this.createIntroPage();
            this.startIntroSequence();
            // Mark intro as seen for this session
            sessionStorage.setItem('nichely_intro_seen', 'true');
        } else {
            // Skip intro and show main page directly with gentle animation
            this.showMainPageDirectly();
        }
    }

    createIntroPage() {
        // Hide main content initially with smooth transition
        const mainContent = document.querySelector('.container');
        if (mainContent) {
            mainContent.style.opacity = '0';
            mainContent.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                mainContent.style.display = 'none';
            }, 300);
        }

        // Create intro page element
        this.introElement = document.createElement('div');
        this.introElement.className = 'intro-page';
        this.introElement.innerHTML = `
            <!-- Sparkle Background -->
            <div class="intro-sparkles">
                <div class="sparkle"></div>
                <div class="sparkle"></div>
                <div class="sparkle"></div>
                <div class="sparkle"></div>
                <div class="sparkle"></div>
                <div class="sparkle"></div>
            </div>

            <!-- Main Content -->
            <img src="/static/src.webp" alt="Nichely Logo" class="intro-logo" 
                 onload="console.log('✅ Logo loaded successfully')" 
                 onerror="console.warn('⚠️ Logo failed to load'); this.style.display='none'">
            <h1 class="intro-title">Nichely</h1>
            <p class="intro-subtitle">Discover AI-powered startup opportunities from real market discussions</p>
            
            <!-- Progress Bar -->
            <div class="intro-progress">
                <div class="intro-progress-bar"></div>
            </div>

            <!-- Skip Button (appears after 1 second) -->
            <button class="skip-button" onclick="introManager.skipIntro()" style="
                position: absolute;
                top: 2rem;
                right: 2rem;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                font-size: 0.9rem;
                cursor: pointer;
                opacity: 0;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                animation: skipButtonShow 0.5s ease-out 1s forwards;
            " onmouseover="this.style.background='rgba(255, 255, 255, 0.3)'" 
               onmouseout="this.style.background='rgba(255, 255, 255, 0.2)'">
                Skip Intro ⏭
            </button>
        `;

        // Add CSS animation for skip button
        const style = document.createElement('style');
        style.textContent = `
            @keyframes skipButtonShow {
                0% {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);

        // Add to page
        document.body.appendChild(this.introElement);
        
        // Prevent scrolling during intro
        document.body.style.overflow = 'hidden';
    }

    startIntroSequence() {
        console.log('🎬 Starting Nichely intro sequence...');

        // Auto-skip after intro duration
        this.skipTimeout = setTimeout(() => {
            this.completeIntro();
        }, this.introDuration);

        // Optional: Add click anywhere to skip after 2 seconds
        setTimeout(() => {
            if (this.introElement) {
                this.introElement.addEventListener('click', () => {
                    this.skipIntro();
                });
                this.introElement.style.cursor = 'pointer';
            }
        }, 2000);
    }

    skipIntro() {
        console.log('⏭ Skipping intro...');
        if (this.skipTimeout) {
            clearTimeout(this.skipTimeout);
        }
        this.completeIntro();
    }

    completeIntro() {
        if (!this.introElement) return;

        console.log('✨ Completing intro transition...');

        // Start fade out animation
        this.introElement.classList.add('fade-out');

        // Remove intro and show main content after animation
        setTimeout(() => {
            this.showMainPage();
            this.cleanupIntro();
        }, 1000);
    }

    showMainPage() {
        const mainContent = document.querySelector('.container');
        if (mainContent) {
            mainContent.style.display = 'block';
            mainContent.style.opacity = '0';
            mainContent.style.transform = 'translateY(30px)';
            
            // Animate main content in with better timing
            requestAnimationFrame(() => {
                mainContent.style.transition = 'all 1s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                mainContent.style.opacity = '1';
                mainContent.style.transform = 'translateY(0)';
            });
        }

        // Focus on search input after transition
        setTimeout(() => {
            const searchInput = document.getElementById('keyword');
            if (searchInput) {
                searchInput.focus();
                console.log('🔍 Ready for search!');
            }
        }, 900);
    }

    cleanupIntro() {
        if (this.introElement && this.introElement.parentNode) {
            this.introElement.parentNode.removeChild(this.introElement);
            this.introElement = null;
        }
        
        // Restore scrolling
        document.body.style.overflow = '';
        
        console.log('🚀 Nichely is ready!');
    }

    showMainPageDirectly() {
        const mainContent = document.querySelector('.container');
        if (mainContent) {
            mainContent.style.display = 'block';
            mainContent.style.opacity = '0';
            mainContent.style.transform = 'translateY(10px)';
            
            // Quick fade-in for returning users
            requestAnimationFrame(() => {
                mainContent.style.transition = 'all 0.6s ease-out';
                mainContent.style.opacity = '1';
                mainContent.style.transform = 'translateY(0)';
            });
        }

        // Focus on search input
        setTimeout(() => {
            const searchInput = document.getElementById('keyword');
            if (searchInput) {
                searchInput.focus();
            }
        }, 700);
    }

    // Force show intro (for development/testing)
    forceShowIntro() {
        sessionStorage.removeItem('nichely_intro_seen');
        location.reload();
    }

    // Reset intro for next session
    resetIntro() {
        sessionStorage.removeItem('nichely_intro_seen');
        console.log('🔄 Intro reset for next visit');
    }
}

// Global intro manager instance
const introManager = new IntroManager();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        try {
            introManager.init();
        } catch (error) {
            console.error('❌ Intro initialization failed:', error);
            introManager.showMainPage(); // Fallback to main page
        }
    });
} else {
    try {
        introManager.init();
    } catch (error) {
        console.error('❌ Intro initialization failed:', error);
        introManager.showMainPage(); // Fallback to main page
    }
}

// Global functions for easy access
window.introManager = introManager;
window.skipIntro = () => introManager.skipIntro();
window.forceShowIntro = () => introManager.forceShowIntro();
window.resetIntro = () => introManager.resetIntro();

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Press 'Escape' or 'Space' to skip intro
    if ((e.code === 'Escape' || e.code === 'Space') && introManager.introElement) {
        e.preventDefault();
        introManager.skipIntro();
    }
    
    // Press 'R' to replay intro (for development)
    if (e.code === 'KeyR' && e.ctrlKey) {
        e.preventDefault();
        introManager.forceShowIntro();
    }
});

// Development helper: Show intro controls in console
console.log(`
🎬 Nichely Intro Controls:
• Press ESC or SPACE to skip intro
• Press Ctrl+R to replay intro
• Type introManager.forceShowIntro() to replay
• Type introManager.resetIntro() to reset for next visit
`);