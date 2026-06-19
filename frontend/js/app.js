const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    loadRecommendations();
    loadAllCourses();
});

async function loadRecommendations() {
    const container = document.getElementById('recommendations-container');
    container.innerHTML = '<div class="loader-container"><span class="loader"></span></div>';
    
    try {
        const response = await fetch(`${API_BASE}/recommendations`);
        const courses = await response.json();
        renderCourses(courses, container, true);
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        container.innerHTML = '<p style="text-align:center; color: #ef4444; width: 100%;">Failed to load recommendations. Make sure backend is running.</p>';
    }
}

async function loadAllCourses() {
    const container = document.getElementById('all-courses-container');
    container.innerHTML = '<div class="loader-container"><span class="loader"></span></div>';
    
    try {
        const response = await fetch(`${API_BASE}/courses`);
        const courses = await response.json();
        renderCourses(courses, container, false);
    } catch (error) {
        console.error('Error fetching all courses:', error);
        container.innerHTML = '<p style="text-align:center; color: #ef4444; width: 100%;">Failed to load courses. Make sure backend is running.</p>';
    }
}

async function enrollCourse(courseId, btnElement) {
    btnElement.innerHTML = 'Enrolling...';
    btnElement.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/enroll`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ course_id: courseId })
        });
        
        if (response.ok) {
            btnElement.innerHTML = 'Enrolled';
            btnElement.classList.add('enrolled');
            // Refresh recommendations based on new enrollment
            loadRecommendations();
        } else {
            throw new Error('Failed to enroll');
        }
    } catch (error) {
        console.error('Error enrolling:', error);
        btnElement.innerHTML = 'Failed';
        setTimeout(() => {
            btnElement.innerHTML = 'Enroll Now';
            btnElement.disabled = false;
        }, 2000);
    }
}

function renderCourses(courses, container, isRecommendation) {
    if (!courses || courses.length === 0) {
        container.innerHTML = '<p style="text-align:center; width: 100%;">No courses found.</p>';
        return;
    }

    container.innerHTML = '';
    
    courses.forEach((course, index) => {
        // Create tags html
        const tagsHtml = course.tags ? course.tags.split(',').map(tag => `<span class="tag">${tag.trim()}</span>`).join('') : '';
        
        // Add animation delay for stagger effect
        const delay = index * 0.1;
        
        const courseCard = document.createElement('div');
        courseCard.className = 'course-card glass-card slide-up';
        courseCard.style.animationDelay = `${delay}s`;
        
        courseCard.innerHTML = `
            <div class="course-category">${course.category}</div>
            <h3 class="course-title">${course.title}</h3>
            <p class="course-desc">${course.description}</p>
            <div class="course-tags">
                ${tagsHtml}
            </div>
            <div class="course-footer">
                ${isRecommendation ? '<span style="font-size:0.8rem; color: #10b981;">✨ ML Suggested</span>' : '<span></span>'}
                <a href="course.html?id=${course.id}" class="enroll-btn" style="text-decoration:none; display:inline-block; text-align:center;">View Course</a>
            </div>
        `;
        
        container.appendChild(courseCard);
    });
}
