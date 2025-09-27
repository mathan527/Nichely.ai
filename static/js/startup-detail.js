// JavaScript to load startup data from localStorage on detail page
document.addEventListener('DOMContentLoaded', function() {
    // Show loading page
    if (window.loadingManager) {
        window.loadingManager.show();
    }
    
    const urlPath = window.location.pathname;
    const encodedStartupId = urlPath.split('/startup/')[1];
    const startupId = decodeURIComponent(encodedStartupId);
    
    console.log('Loading startup detail for ID:', startupId);
    console.log('Original encoded ID:', encodedStartupId);
    
    // Get startup data from localStorage
    const storedData = localStorage.getItem('currentStartupIdeas');
    if (!storedData) {
        console.error('No startup data found in localStorage');
        // Hide loading on error
        if (window.loadingManager) {
            window.loadingManager.hide();
        }
        showError('No startup data found. Please go back and search again.');
        return;
    }
    
    let startupData;
    try {
        const allStartups = JSON.parse(storedData);
        startupData = allStartups[startupId];
        
        if (!startupData) {
            console.error('Startup ID not found:', startupId);
            console.log('Available IDs:', Object.keys(allStartups));
            // Hide loading on error
            if (window.loadingManager) {
                window.loadingManager.hide();
            }
            showError(`Startup "${startupId}" not found. Available startups: ${Object.keys(allStartups).join(', ')}`);
            return;
        }
        
        console.log('Found startup data:', startupData);
        console.log('Available startup fields:', Object.keys(startupData));
        console.log('Pain points field:', startupData.pain_points);
        console.log('Problem statement field:', startupData.problem_statement);
        console.log('Solution highlights field:', startupData.solution_highlights);
        console.log('Target market field:', startupData.target_market);
        console.log('Technology stack field:', startupData.technology_stack);
        
        // Populate details and then complete loading
        populateStartupDetails(startupData);
        
        // Complete loading after data is populated
        setTimeout(() => {
            if (window.loadingManager) {
                window.loadingManager.complete();
            }
        }, 1200);
        
    } catch (error) {
        console.error('Error parsing startup data:', error);
        // Hide loading on error
        if (window.loadingManager) {
            window.loadingManager.hide();
        }
        showError('Error loading startup data. Please try again.');
    }
});

function populateStartupDetails(startup) {
    console.log('Populating startup details with data:', startup);
    
    // Update page title
    document.title = `${startup.name} - Detailed Analysis`;
    
    // Update main header section
    const h1 = document.querySelector('h1');
    if (h1) {
        h1.textContent = startup.name || 'Startup Analysis';
        console.log('Updated h1:', startup.name);
    }
    
    const taglineEl = document.querySelector('p.text-xl.text-gray-600');
    if (taglineEl) {
        taglineEl.textContent = startup.tagline || startup.description || 'Innovative startup solution';
        console.log('Updated tagline:', startup.tagline);
    }
    
    // Update key metrics in header (if they exist in template)
    updateMetricsHeaderIfExists(startup.metrics);
    
    // Update all content sections
    updateAllSections(startup);
    
    console.log('Startup details populated successfully');
}

function updateElement(selector, content) {
    const element = document.querySelector(selector);
    if (element && content) {
        element.textContent = content;
        console.log(`Updated ${selector} with:`, content);
    } else {
        console.log(`Could not find element with selector: ${selector}`);
    }
}

function getTagline(startup) {
    return startup.tagline || 
           startup.description || 
           `Innovative solution for the ${startup.name.toLowerCase()} market`;
}

function updateProblemStatements(problems) {
    // Create or update problem statement section
    let problemSection = document.querySelector('#problemStatementsSection');
    if (!problemSection) {
        const container = document.querySelector('.container') || document.body;
        problemSection = document.createElement('div');
        problemSection.id = 'problemStatementsSection';
        problemSection.className = 'bg-white rounded-xl shadow-sm p-6 mt-8';
        problemSection.innerHTML = `
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Problem Statement</h2>
            <div id="problemsList" class="space-y-4"></div>
        `;
        container.appendChild(problemSection);
    }
    
    const problemsList = document.querySelector('#problemsList');
    if (!problemsList) return;
    
    problemsList.innerHTML = '';
    
    const problemsArray = Array.isArray(problems) ? problems : (problems ? [problems] : ['Market opportunity identified through analysis']);
    
    problemsArray.forEach(problem => {
        if (problem && typeof problem === 'string') {
            const div = document.createElement('div');
            div.className = 'bg-red-50 rounded-lg p-4 mb-4';
            div.innerHTML = `<p class="text-red-800">${problem}</p>`;
            problemsList.appendChild(div);
        }
    });
}

function updatePainPoints(painPoints) {
    console.log('updatePainPoints called with:', painPoints);
    console.log('painPoints type:', typeof painPoints);
    console.log('painPoints is array:', Array.isArray(painPoints));
    
    // This is our key feature - detailed pain points display
    const container = document.querySelector('#painPointsSection') || 
                     document.querySelector('[data-section="pain-points"]');
    
    if (!container) {
        // Create pain points section if it doesn't exist
        const mainContent = document.querySelector('.container') || document.body;
        const section = document.createElement('div');
        section.id = 'painPointsSection';
        section.className = 'bg-white rounded-xl shadow-sm p-6 mt-8';
        section.innerHTML = `
            <h2 class="text-2xl font-bold text-gray-900 mb-4">🎯 Pain Points Analysis</h2>
            <div id="painPointsList"></div>
        `;
        mainContent.appendChild(section);
    }
    
    const listContainer = document.querySelector('#painPointsList');
    if (!listContainer) return;
    
    listContainer.innerHTML = '';
    
    // Handle different data structures
    let painPointsArray = [];
    
    if (Array.isArray(painPoints)) {
        painPointsArray = painPoints;
    } else if (typeof painPoints === 'string') {
        painPointsArray = [painPoints];
    } else if (painPoints && typeof painPoints === 'object') {
        // Handle object structures like {point: "text", ...}
        painPointsArray = Object.values(painPoints).filter(p => typeof p === 'string');
    }
    
    console.log('Processing pain points array:', painPointsArray);
    
    if (painPointsArray.length === 0) {
        listContainer.innerHTML = `
            <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-gray-600">No specific pain points identified for this startup idea.</p>
            </div>`;
        return;
    }
    
    painPointsArray.forEach((painPoint, index) => {
        if (painPoint && typeof painPoint === 'string') {
            const div = document.createElement('div');
            div.className = 'bg-orange-50 border-l-4 border-orange-400 rounded-lg p-4 mb-3';
            div.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-orange-100 text-orange-600 font-semibold text-sm">
                            ${index + 1}
                        </span>
                    </div>
                    <div class="ml-3">
                        <p class="text-orange-800 font-medium">${painPoint}</p>
                    </div>
                </div>
            `;
            listContainer.appendChild(div);
        }
    });
}

function updateSolutionHighlights(solutions) {
    // Create or update solution section
    let solutionSection = document.querySelector('#solutionSection');
    if (!solutionSection) {
        const container = document.querySelector('.container') || document.body;
        solutionSection = document.createElement('div');
        solutionSection.id = 'solutionSection';
        solutionSection.className = 'bg-white rounded-xl shadow-sm p-6 mt-8';
        solutionSection.innerHTML = `
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Solution</h2>
            <div id="solutionsList" class="space-y-4"></div>
        `;
        container.appendChild(solutionSection);
    }
    
    const solutionsList = document.querySelector('#solutionsList');
    if (!solutionsList) return;
    
    solutionsList.innerHTML = '';
    
    const solutionsArray = Array.isArray(solutions) ? solutions : (solutions ? [solutions] : ['AI-powered solution for market optimization']);
    
    solutionsArray.forEach(solution => {
        if (solution && typeof solution === 'string') {
            const div = document.createElement('div');
            div.className = 'bg-green-50 rounded-lg p-4 mb-4';
            div.innerHTML = `<p class="text-green-800">${solution}</p>`;
            solutionsList.appendChild(div);
        }
    });
}

function updateCompetitiveAdvantages(advantages) {
    const container = document.querySelector('#competitiveAdvantages') || 
                     document.querySelector('[data-section="advantages"]');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    const advantagesArray = Array.isArray(advantages) ? advantages : [advantages];
    
    advantagesArray.forEach(advantage => {
        if (advantage) {
            const div = document.createElement('div');
            div.className = 'bg-purple-50 rounded-lg p-4 mb-4';
            div.innerHTML = `<p class="text-purple-800">${advantage}</p>`;
            container.appendChild(div);
        }
    });
}

function updateMetrics(metrics) {
    // Update metric displays if they exist
    const marketSize = document.querySelector('[data-metric="market_size"]');
    const growthRate = document.querySelector('[data-metric="growth_potential"]');
    const innovation = document.querySelector('[data-metric="innovation_score"]');
    
    if (marketSize && metrics.market_size) {
        marketSize.textContent = `$${(metrics.market_size/1000000).toFixed(1)}M`;
    }
    
    if (growthRate && metrics.growth_potential) {
        growthRate.textContent = `${metrics.growth_potential}%`;
    }
    
    if (innovation && metrics.innovation_score) {
        innovation.textContent = `${metrics.innovation_score}`;
    }
}

function updateAIInsights(startup) {
    const container = document.querySelector('#aiInsights');
    if (!container) return;
    
    const insights = startup.agentic_insights;
    const aiReasoning = startup.ai_reasoning;
    
    if (insights || aiReasoning) {
        container.classList.remove('hidden');
        
        if (insights.confidence_score) {
            const confidence = document.querySelector('#aiConfidence');
            if (confidence) {
                confidence.textContent = `${(insights.confidence_score * 100).toFixed(0)}%`;
            }
        }
        
        if (insights.generated_by_agents) {
            const agents = document.querySelector('#aiAgents');
            if (agents) {
                agents.textContent = insights.generated_by_agents.join(', ');
            }
        }
        
        if (aiReasoning) {
            const reasoning = document.querySelector('#aiReasoning');
            if (reasoning) {
                reasoning.textContent = aiReasoning;
            }
        }
    }
}

function updateMetricsHeaderIfExists(metrics) {
    if (!metrics) return;
    
    console.log('Updating metrics:', metrics);
    
    // Update market size
    const marketSizeEl = document.querySelector('.text-2xl.font-bold.text-blue-900');
    if (marketSizeEl && metrics.market_size) {
        marketSizeEl.textContent = `$${(metrics.market_size/1000000).toFixed(1)}M`;
        console.log('Updated market size');
    }
    
    // Update growth rate  
    const growthEl = document.querySelector('.text-2xl.font-bold.text-green-900');
    if (growthEl && metrics.growth_potential) {
        growthEl.textContent = `${metrics.growth_potential}%`;
        console.log('Updated growth rate');
    }
    
    // Update innovation score
    const innovationEl = document.querySelector('.text-2xl.font-bold.text-purple-900');
    if (innovationEl && metrics.innovation_score) {
        innovationEl.textContent = `${metrics.innovation_score}`;
        console.log('Updated innovation score');
    }
}

function updateAllSections(startup) {
    // Create a comprehensive content area since template might be minimal
    const container = document.querySelector('.container') || document.body;
    
    // Create main content if not exists
    let mainContent = document.querySelector('#dynamicContent');
    if (!mainContent) {
        mainContent = document.createElement('div');
        mainContent.id = 'dynamicContent';
        mainContent.className = 'space-y-8 mt-8';
        container.appendChild(mainContent);
    }
    
    // Clear existing content to avoid duplication
    mainContent.innerHTML = '';
    
    // Add debug section first to see raw data
    addDebugSection(mainContent, startup);
    
    // Add all sections systematically
    addProblemStatementSection(mainContent, startup.problem_statement);
    addPainPointsSection(mainContent, startup.pain_points);
    addSolutionSection(mainContent, startup.solution_highlights);
    addTechnologySection(mainContent, startup.technology_stack);
    addTargetMarketSection(mainContent, startup.target_market);
    addMetricsSection(mainContent, startup.metrics);
    
    if (startup.agentic_insights) {
        addAIInsightsSection(mainContent, startup.agentic_insights, startup.ai_reasoning);
    }
}

function addDebugSection(container, startup) {
    const section = document.createElement('div');
    section.className = 'bg-gray-100 rounded-xl shadow-sm p-6';
    section.innerHTML = `
        <h2 class="text-2xl font-bold text-gray-900 mb-4">🔍 Debug: Raw Data Structure</h2>
        <pre class="text-sm bg-white p-4 rounded overflow-auto max-h-96">${JSON.stringify(startup, null, 2)}</pre>
    `;
    container.appendChild(section);
}

function updateTechnologyStack(techStack) {
    // Handle both object and simple array formats
    const coretech = techStack?.core_technologies || 
                    techStack?.technology || 
                    ['Python', 'React', 'PostgreSQL'];
                    
    const infrastructure = techStack?.infrastructure || 
                          ['AWS', 'Docker'];
    
    // Create or update technology stack section
    let techSection = document.querySelector('#technologyStackSection');
    if (!techSection) {
        // Create the section if it doesn't exist
        const container = document.querySelector('.container') || document.body;
        techSection = document.createElement('div');
        techSection.id = 'technologyStackSection';
        techSection.className = 'bg-white rounded-xl shadow-sm p-6 mt-8';
        techSection.innerHTML = `
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Technology Stack</h2>
            <div class="grid grid-cols-2 gap-6">
                <div>
                    <h3 class="font-semibold text-gray-700 mb-3">Core Technologies</h3>
                    <ul id="coreTechList" class="space-y-2"></ul>
                </div>
                <div>
                    <h3 class="font-semibold text-gray-700 mb-3">Infrastructure</h3>
                    <ul id="infraList" class="space-y-2"></ul>
                </div>
            </div>
        `;
        container.appendChild(techSection);
    }
    
    // Update core technologies
    const coreTechList = document.querySelector('#coreTechList');
    if (coreTechList) {
        coreTechList.innerHTML = coretech.map(tech => `
            <li class="flex items-center text-gray-600">
                <svg class="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                ${tech}
            </li>
        `).join('');
    }
    
    // Update infrastructure
    const infraList = document.querySelector('#infraList');
    if (infraList) {
        infraList.innerHTML = infrastructure.map(infra => `
            <li class="flex items-center text-gray-600">
                <svg class="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                ${infra}
            </li>
        `).join('');
    }
}

function updateTargetMarket(targetMarket) {
    // Handle both object and simple formats
    const segments = targetMarket?.segments || ['SMB', 'Enterprise'];
    const marketSize = targetMarket?.size || 1000000;
    const growthRate = targetMarket?.growth_rate || '25% YoY';
    const geography = targetMarket?.geography || 'Global';
    
    // Create or update target market section
    let marketSection = document.querySelector('#targetMarketSection');
    if (!marketSection) {
        const container = document.querySelector('.container') || document.body;
        marketSection = document.createElement('div');
        marketSection.id = 'targetMarketSection';
        marketSection.className = 'bg-white rounded-xl shadow-sm p-6 mt-8';
        marketSection.innerHTML = `
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Target Market</h2>
            <div class="grid grid-cols-2 gap-6">
                <div>
                    <h3 class="font-semibold text-gray-700 mb-3">Segments</h3>
                    <ul id="segmentsList" class="space-y-2"></ul>
                </div>
                <div>
                    <h3 class="font-semibold text-gray-700 mb-3">Key Metrics</h3>
                    <ul id="metricsList" class="space-y-2"></ul>
                </div>
            </div>
        `;
        container.appendChild(marketSection);
    }
    
    // Update segments
    const segmentsList = document.querySelector('#segmentsList');
    if (segmentsList) {
        segmentsList.innerHTML = segments.map(segment => `
            <li class="flex items-center text-gray-600">
                <svg class="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                ${segment}
            </li>
        `).join('');
    }
    
    // Update key metrics
    const metricsList = document.querySelector('#metricsList');
    if (metricsList) {
        metricsList.innerHTML = `
            <li class="flex items-center text-gray-600">
                <span class="font-medium mr-2">Market Size:</span>
                $${marketSize.toLocaleString()}
            </li>
            <li class="flex items-center text-gray-600">
                <span class="font-medium mr-2">Growth Rate:</span>
                ${growthRate}
            </li>
            <li class="flex items-center text-gray-600">
                <span class="font-medium mr-2">Geography:</span>
                ${geography}
            </li>
        `;
    }
}

function addProblemStatementSection(container, problems) {
    const problemsArray = Array.isArray(problems) ? problems : (problems ? [problems] : ['Market opportunity identified']);
    
    const section = document.createElement('div');
    section.className = 'bg-white rounded-xl shadow-sm p-6';
    section.innerHTML = `
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Problem Statement</h2>
        <div class="space-y-4">
            ${problemsArray.map(problem => `
                <div class="bg-red-50 rounded-lg p-4">
                    <p class="text-red-800">${problem}</p>
                </div>
            `).join('')}
        </div>
    `;
    container.appendChild(section);
}

function addPainPointsSection(container, painPoints) {
    const painPointsArray = Array.isArray(painPoints) ? painPoints : [];
    
    if (painPointsArray.length === 0) return;
    
    const section = document.createElement('div');
    section.className = 'bg-white rounded-xl shadow-sm p-6';
    section.innerHTML = `
        <h2 class="text-2xl font-bold text-gray-900 mb-4">🎯 Detailed Pain Points Analysis</h2>
        <div class="space-y-3">
            ${painPointsArray.map((painPoint, index) => `
                <div class="bg-orange-50 border-l-4 border-orange-400 rounded-lg p-4">
                    <div class="flex items-start">
                        <div class="flex-shrink-0">
                            <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-orange-100 text-orange-600 font-semibold text-sm">
                                ${index + 1}
                            </span>
                        </div>
                        <div class="ml-3">
                            <p class="text-orange-800 font-medium">${painPoint}</p>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    container.appendChild(section);
}

function addSolutionSection(container, solutions) {
    const solutionsArray = Array.isArray(solutions) ? solutions : (solutions ? [solutions] : ['AI-powered solution']);
    
    const section = document.createElement('div');
    section.className = 'bg-white rounded-xl shadow-sm p-6';
    section.innerHTML = `
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Solution</h2>
        <div class="space-y-4">
            ${solutionsArray.map(solution => `
                <div class="bg-green-50 rounded-lg p-4">
                    <p class="text-green-800">${solution}</p>
                </div>
            `).join('')}
        </div>
    `;
    container.appendChild(section);
}

function addTechnologySection(container, techStack) {
    const coretech = techStack?.core_technologies || ['Python', 'React', 'PostgreSQL'];
    const infrastructure = techStack?.infrastructure || ['AWS', 'Docker'];
    
    const section = document.createElement('div');
    section.className = 'bg-white rounded-xl shadow-sm p-6';
    section.innerHTML = `
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Technology Stack</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h3 class="font-semibold text-gray-700 mb-3">Core Technologies</h3>
                <ul class="space-y-2">
                    ${coretech.map(tech => `
                        <li class="flex items-center text-gray-600">
                            <svg class="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                            </svg>
                            ${tech}
                        </li>
                    `).join('')}
                </ul>
            </div>
            <div>
                <h3 class="font-semibold text-gray-700 mb-3">Infrastructure</h3>
                <ul class="space-y-2">
                    ${infrastructure.map(infra => `
                        <li class="flex items-center text-gray-600">
                            <svg class="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                            </svg>
                            ${infra}
                        </li>
                    `).join('')}
                </ul>
            </div>
        </div>
    `;
    container.appendChild(section);
}

function addTargetMarketSection(container, targetMarket) {
    const segments = targetMarket?.segments || ['SMB', 'Enterprise'];
    const marketSize = targetMarket?.size || 1000000;
    const growthRate = targetMarket?.growth_rate || '25% YoY';
    const geography = targetMarket?.geography || 'Global';
    
    const section = document.createElement('div');
    section.className = 'bg-white rounded-xl shadow-sm p-6';
    section.innerHTML = `
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Target Market</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h3 class="font-semibold text-gray-700 mb-3">Segments</h3>
                <ul class="space-y-2">
                    ${segments.map(segment => `
                        <li class="flex items-center text-gray-600">
                            <svg class="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                            </svg>
                            ${segment}
                        </li>
                    `).join('')}
                </ul>
            </div>
            <div>
                <h3 class="font-semibold text-gray-700 mb-3">Key Metrics</h3>
                <ul class="space-y-2">
                    <li class="flex items-center text-gray-600">
                        <span class="font-medium mr-2">Market Size:</span>
                        $${marketSize.toLocaleString()}
                    </li>
                    <li class="flex items-center text-gray-600">
                        <span class="font-medium mr-2">Growth Rate:</span>
                        ${growthRate}
                    </li>
                    <li class="flex items-center text-gray-600">
                        <span class="font-medium mr-2">Geography:</span>
                        ${geography}
                    </li>
                </ul>
            </div>
        </div>
    `;
    container.appendChild(section);
}

function addMetricsSection(container, metrics) {
    if (!metrics) return;
    
    const section = document.createElement('div');
    section.className = 'bg-white rounded-xl shadow-sm p-6';
    section.innerHTML = `
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Key Metrics</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-blue-50 rounded-lg p-4 text-center">
                <div class="text-blue-800 font-medium mb-1">Market Size</div>
                <div class="text-2xl font-bold text-blue-900">$${(metrics.market_size/1000000).toFixed(1)}M</div>
            </div>
            <div class="bg-green-50 rounded-lg p-4 text-center">
                <div class="text-green-800 font-medium mb-1">Growth Rate</div>
                <div class="text-2xl font-bold text-green-900">${metrics.growth_potential}%</div>
            </div>
            <div class="bg-purple-50 rounded-lg p-4 text-center">
                <div class="text-purple-800 font-medium mb-1">Innovation Score</div>
                <div class="text-2xl font-bold text-purple-900">${metrics.innovation_score}</div>
            </div>
        </div>
    `;
    container.appendChild(section);
}

function addAIInsightsSection(container, insights, reasoning) {
    const section = document.createElement('div');
    section.className = 'bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl shadow-sm p-6 border border-blue-200';
    section.innerHTML = `
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <svg class="w-7 h-7 mr-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            Agentic AI Analysis
            <span class="ml-auto text-sm text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
                ${(insights.confidence_score * 100).toFixed(0)}% confidence
            </span>
        </h2>
        <p class="text-blue-700 text-sm mb-4">${reasoning || "Advanced AI analysis provided comprehensive market insights."}</p>
        <div class="text-xs text-blue-600">
            Generated by: ${insights.generated_by_agents?.join(', ') || 'AI Agents'}
        </div>
    `;
    container.appendChild(section);
}

function showError(message) {
    const container = document.querySelector('.container') || document.body;
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-50 border-l-4 border-red-500 p-4 mb-8';
    errorDiv.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                </svg>
            </div>
            <div class="ml-3">
                <p class="text-sm text-red-700">${message}</p>
                <div class="mt-2">
                    <a href="/" class="text-sm text-red-600 hover:text-red-800 underline">← Back to Search</a>
                </div>
            </div>
        </div>
    `;
    container.insertBefore(errorDiv, container.firstChild);
}