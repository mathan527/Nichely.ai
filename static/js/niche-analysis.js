// Function to fetch and display leaderboard
function updateLeaderboard() {
    fetch('/leaderboard')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Ensure data is an array, if not make it an empty array
            const entries = Array.isArray(data) ? data : [];
            
            if (entries.length === 0) {
                document.getElementById('leaderboard').innerHTML = `
                    <div class="p-4 text-center text-gray-500">
                        No searches recorded yet. Be the first to analyze a niche!
                    </div>`;
                return;
            }
            
            const leaderboardHtml = entries.map((entry, index) => `
                <div class="leaderboard-item ${index < 3 ? 'top-three' : ''} p-3 mb-2 bg-white rounded shadow-sm">
                    <span class="rank font-bold">#${index + 1}</span>
                    <span class="keyword text-blue-600">${entry.keyword}</span>
                    <span class="searches text-gray-600">${entry.search_count} searches</span>
                    <span class="last-search text-gray-500 text-sm">
                        Last: ${new Date(entry.last_searched).toLocaleDateString()}
                    </span>
                    <div class="mt-2 text-sm">
                        <span class="text-gray-600">Market Potential: </span>
                        <span class="font-medium text-blue-600">${Math.round(entry.market_potential)}%</span>
                    </div>
                </div>
            `).join('');
            
            document.getElementById('leaderboard').innerHTML = leaderboardHtml;
        })
        .catch(error => {
            console.error('Error fetching leaderboard:', error);
            document.getElementById('leaderboard').innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    Unable to load leaderboard. Please try again later.
                </div>`;
        });
}

function showLoading() {
    // Show professional loading page
    if (typeof window.showLoading !== 'undefined' && window.loadingManager) {
        window.loadingManager.show();
    }
    
    // Hide other elements
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
}

function showError(message) {
    // Hide professional loading page
    if (window.loadingManager) {
        window.loadingManager.hide();
    }
    
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.remove('hidden');
    document.getElementById('errorMessage').textContent = message;
}

function showResults() {
    // Complete and hide loading page
    if (window.loadingManager) {
        window.loadingManager.complete();
    }
    
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('results').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
}

function displayNicheIdeas(startupIdeas) {
    if (!startupIdeas || !Array.isArray(startupIdeas)) {
        console.warn('No startup ideas received or invalid format');
        document.getElementById('nicheIdeas').innerHTML = `
            <div class="p-8 text-center text-gray-500 bg-white rounded-lg shadow-md">
                <h3 class="text-xl font-semibold mb-2">No AI Ideas Generated</h3>
                <p>Try a different keyword or check your connection.</p>
            </div>`;
        return;
    }

    const container = document.getElementById('nicheIdeas');
    const template = document.getElementById('startupCardTemplate');
    container.innerHTML = '';
    
    // Ensure exactly 5 ideas are displayed
    const ideasToShow = startupIdeas.slice(0, 5);
    console.log(`Displaying ${ideasToShow.length} startup ideas`);
    
    // Store all startup ideas in localStorage for detail page access
    const storageData = {};
    ideasToShow.forEach((idea, index) => {
        const ideaId = idea.id || `idea-${index + 1}`;
        storageData[ideaId] = idea;
    });
    
    // Save to localStorage
    localStorage.setItem('currentStartupIdeas', JSON.stringify(storageData));
    console.log('Startup ideas saved to localStorage:', Object.keys(storageData));
    console.log('Full storage data structure:', storageData);
    console.log('Sample idea structure:', ideasToShow[0]);
    
    ideasToShow.forEach((idea, index) => {
        // Get problem statement (first one if array, or direct string)
        const problemStatement = Array.isArray(idea.problem_statement) ? 
            idea.problem_statement[0] : 
            idea.problem_statement || 'Market opportunity identified through AI analysis';

        // Create idea ID
        const ideaId = idea.id || `idea-${index + 1}`;

        // Clone template and replace variables
        let html = template.innerHTML
            .replace(/{id}/g, ideaId)
            .replace('{name}', idea.name || `Startup Idea ${index + 1}`)
            .replace('{problemStatement}', problemStatement);

        // Add to container
        container.insertAdjacentHTML('beforeend', html);
    });

    console.log('All startup idea boxes displayed successfully');
}

// Function to handle navigation to startup detail page
function goToStartupDetail(ideaId) {
    console.log(`Navigating to startup detail: ${ideaId}`);
    window.location.href = `/startup/${ideaId}`;
}

function displayDiscussions(discussions) {
    const discussionsHtml = discussions.map(discussion => `
        <div class="discussion-item p-4 bg-gray-50 rounded-lg">
            <p class="text-gray-700">${discussion}</p>
        </div>
    `).join('');
    document.getElementById('discussions').innerHTML = discussionsHtml;
}

function displayVisualizations(visualizations) {
    if (!visualizations) {
        console.warn('No visualization data received');
        // Hide visualization containers if no data
        const sentimentChart = document.getElementById('sentimentChart');
        const topicsChart = document.getElementById('topicsChart');
        if (sentimentChart) sentimentChart.style.display = 'none';
        if (topicsChart) topicsChart.style.display = 'none';
        return;
    }

    // Display sentiment chart
    const sentimentChart = document.getElementById('sentimentChart');
    if (visualizations.sentiment_pie) {
        console.log('Setting sentiment chart');
        sentimentChart.src = `data:image/png;base64,${visualizations.sentiment_pie}`;
        sentimentChart.style.display = 'block';
        sentimentChart.classList.remove('hidden');
    } else {
        console.warn('No sentiment_pie data received');
        sentimentChart.style.display = 'none';
    }
    
    // Display word frequency chart
    const topicsChart = document.getElementById('topicsChart');
    if (visualizations.word_freq) {
        console.log('Setting word frequency chart');
        topicsChart.src = `data:image/png;base64,${visualizations.word_freq}`;
        topicsChart.style.display = 'block';
        topicsChart.classList.remove('hidden');
    } else {
        console.warn('No word_freq data received');
        topicsChart.style.display = 'none';
    }
}

async function analyzeNiche() {
    const keyword = document.getElementById('keyword').value.trim();
    if (!keyword) {
        showError('Please enter a keyword');
        return;
    }

    if (keyword.length < 2) {
        showError('Keyword must be at least 2 characters long');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`/niche/${encodeURIComponent(keyword)}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Analysis Response:', data);
        
        // Display AI-generated startup ideas
        if (data.startup_ideas && Array.isArray(data.startup_ideas)) {
            displayNicheIdeas(data.startup_ideas);
        } else {
            console.warn('No startup ideas or invalid format received');
            document.getElementById('nicheIdeas').innerHTML = `
                <div class="p-8 text-center text-yellow-600 bg-yellow-50 rounded-lg border border-yellow-200">
                    <h3 class="text-xl font-semibold mb-2">⚠️ No Ideas Generated</h3>
                    <p>AI couldn't generate ideas for this keyword. Try a more specific niche.</p>
                </div>`;
        }
        
        // Display visualizations if available
        if (data.visualizations) {
            displayVisualizations(data.visualizations);
        }
        
        showResults();
        
        // Update leaderboard after successful analysis
        updateLeaderboard();
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError('Failed to analyze niche: ' + error.message);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    // Load initial leaderboard
    updateLeaderboard();
    
    // Add enter key support
    document.getElementById('keyword').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            analyzeNiche();
        }
    });
});