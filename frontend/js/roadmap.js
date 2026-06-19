const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    const searchBox = document.getElementById('roadmap-search');
    
    // Load a default roadmap
    fetchRoadmap('web development');

    let debounceTimer;
    searchBox.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = e.target.value.trim();
            if (query.length > 2) {
                fetchRoadmap(query);
            }
        }, 500);
    });
});

async function fetchRoadmap(query) {
    document.getElementById('roadmap-content').style.display = 'none';
    document.getElementById('loading').style.display = 'flex';

    try {
        const response = await fetch(`${API_BASE}/roadmap?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        document.getElementById('loading').style.display = 'none';
        
        document.getElementById('roadmap-domain').innerText = data.domain + " Roadmap";
        
        const container = document.getElementById('timeline-container');
        container.innerHTML = '';
        
        data.steps.forEach((step, index) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'timeline-step slide-up';
            stepDiv.style.animationDelay = `${index * 0.1}s`;
            
            stepDiv.innerHTML = `
                <div class="timeline-content glass-card">
                    <h3>Step ${index + 1}: ${step.title}</h3>
                    <p style="color: var(--text-secondary);">${step.desc}</p>
                </div>
            `;
            container.appendChild(stepDiv);
        });
        
        document.getElementById('roadmap-content').style.display = 'block';
    } catch (error) {
        console.error(error);
        document.getElementById('loading').style.display = 'none';
    }
}
