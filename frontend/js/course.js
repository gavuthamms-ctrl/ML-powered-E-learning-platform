const API_BASE = '/api';
const urlParams = new URLSearchParams(window.location.search);
const courseId = urlParams.get('id');

document.addEventListener('DOMContentLoaded', () => {
    if (!courseId) {
        document.getElementById('course-title').innerText = "Course not found";
        return;
    }
    loadCourseDetails();

    document.getElementById('enroll-btn').addEventListener('click', enrollInCourse);
});

async function loadCourseDetails() {
    try {
        const response = await fetch(`${API_BASE}/courses/${courseId}`);
        if (!response.ok) throw new Error("Course not found");
        const course = await response.json();

        document.getElementById('course-category').innerText = course.category;
        document.getElementById('course-title').innerText = course.title;
        document.getElementById('course-desc').innerText = course.description;
        document.getElementById('course-duration').innerText = `Duration: ${course.duration || 'Flexible'}`;

        const tagsContainer = document.getElementById('course-tags');
        if (course.tags) {
            tagsContainer.innerHTML = course.tags.split(',').map(tag => `<span class="tag">${tag.trim()}</span>`).join('');
        }

        const modulesList = document.getElementById('modules-list');
        modulesList.innerHTML = '';
        if (course.modules && course.modules.length > 0) {
            course.modules.forEach(mod => {
                const li = document.createElement('li');
                li.innerText = mod.trim();
                modulesList.appendChild(li);
            });
        } else {
            modulesList.innerHTML = '<li>Content is currently being updated.</li>';
        }
    } catch (error) {
        console.error(error);
        document.getElementById('course-title').innerText = "Failed to load course details.";
    }
}

async function enrollInCourse() {
    const btn = document.getElementById('enroll-btn');
    btn.innerText = "Enrolling...";
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/enroll`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_id: courseId })
        });

        if (response.ok) {
            btn.style.display = 'none';
            document.getElementById('enroll-msg').style.display = 'block';
        } else {
            throw new Error("Enrollment failed");
        }
    } catch (error) {
        console.error(error);
        btn.innerText = "Error. Try again.";
        btn.disabled = false;
    }
}
