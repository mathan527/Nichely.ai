function displayStartupIdeas(data) {
    const container = document.getElementById('startupIdeas');
    if (!container) return;

    // Clear existing content
    container.innerHTML = '';

    if (!data.startup_ideas || data.startup_ideas.length === 0) {
        container.innerHTML = `
            <div class="col-span-full text-center p-8">
                <p class="text-gray-500">No startup ideas found for this niche.</p>
            </div>
        `;
        return;
    }

    // Store all startup ideas in localStorage for detail page access
    const storageData = {};
    data.startup_ideas.forEach(idea => {
        if (idea.id) {
            storageData[idea.id] = idea;
        }
    });
    
    // Save to localStorage
    localStorage.setItem('currentStartupIdeas', JSON.stringify(storageData));
    console.log('Startup ideas saved to localStorage from startup-ideas.js:', Object.keys(storageData));

    // Create cards for each startup idea
    data.startup_ideas.forEach(idea => {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow';
        
        card.innerHTML = `
            <h3 class="text-xl font-semibold mb-4">${escapeHtml(idea.name)}</h3>
            
            <div class="mb-4">
                <h4 class="font-medium text-gray-700">Problem Statement:</h4>
                <p class="text-gray-600">${escapeHtml(idea.problem_statement)}</p>
            </div>
            
            <div class="mb-4">
                <h4 class="font-medium text-gray-700">Solution:</h4>
                <ul class="list-disc pl-5">
                    ${idea.solution.map(point => `<li class="text-gray-600">${escapeHtml(point)}</li>`).join('')}
                </ul>
            </div>
            
            <div class="mb-4">
                <h4 class="font-medium text-gray-700">Pain Points Addressed:</h4>
                <ul class="list-disc pl-5">
                    ${idea.pain_points.map(point => `<li class="text-gray-600">${escapeHtml(point)}</li>`).join('')}
                </ul>
            </div>
            
            <div class="mt-4 pt-4 border-t">
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-500">Market Size: $${numberWithCommas(idea.market_size)}</span>
                    <a href="/startup/${idea.id}" class="text-blue-500 hover:text-blue-700">View Details →</a>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// Helper functions
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Listen for niche analysis completion
document.addEventListener('nicheAnalysisComplete', function(e) {
    if (e.detail && e.detail.data) {
        displayStartupIdeas(e.detail.data);
    }
});