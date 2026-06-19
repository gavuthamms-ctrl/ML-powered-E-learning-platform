const API_BASE = 'http://127.0.0.1:5000/api';

const questions = [
    {
        q: "What is your primary goal for learning?",
        options: ["Start a new career in tech", "Upskill in my current job", "Build my own projects", "Just exploring"]
    },
    {
        q: "Which broad domain interests you the most?",
        options: ["Data Science & AI", "Web Development", "Cyber Security", "Design & UX"]
    },
    {
        q: "What is your current programming experience?",
        options: ["Complete beginner", "Know some basics (loops, variables)", "Comfortable with one language", "Advanced developer"]
    },
    {
        q: "How much time can you dedicate per week?",
        options: ["1-3 hours", "3-5 hours", "5-10 hours", "10+ hours"]
    },
    {
        q: "What type of projects excite you the most?",
        options: ["Building intelligent systems and bots", "Creating beautiful websites and apps", "Hacking and defending networks", "Designing user interfaces"]
    },
    {
        q: "Do you prefer visual creativity or logical problem solving?",
        options: ["Purely visual creativity", "Mostly visual, some logic", "Mostly logic, some visual", "Purely logical problem solving"]
    },
    {
        q: "Which tool or language sounds most appealing to learn?",
        options: ["Python (Pandas, Scikit-learn)", "JavaScript (React, Node)", "Network Scanners (Nmap, Wireshark)", "Design Tools (Figma, Adobe)"]
    },
    {
        q: "How do you prefer to learn?",
        options: ["Reading documentation and theory", "Watching video tutorials", "Hands-on projects", "A mix of everything"]
    },
    {
        q: "Are you interested in managing teams or projects?",
        options: ["Yes, agile and scrum methodologies", "Maybe in the future", "No, I want to be an individual contributor", "Not sure yet"]
    },
    {
        q: "What is your end goal in 6 months?",
        options: ["Land a junior developer role", "Deploy a fully working app", "Get a certification in my field", "Have a strong portfolio"]
    }
];

let currentQuestion = 0;
let userAnswers = [];

document.addEventListener('DOMContentLoaded', () => {
    loadQuestion();
    
    document.getElementById('next-btn').addEventListener('click', () => {
        const selected = document.querySelector('.option-btn.selected');
        if (selected) {
            userAnswers.push(selected.innerText);
            currentQuestion++;
            if (currentQuestion < questions.length) {
                loadQuestion();
            } else {
                submitQuiz();
            }
        }
    });
});

function loadQuestion() {
    const qData = questions[currentQuestion];
    document.getElementById('question-text').innerText = qData.q;
    document.getElementById('question-count').innerText = `Question ${currentQuestion + 1} of ${questions.length}`;
    
    const progress = ((currentQuestion) / questions.length) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;

    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';
    
    const nextBtn = document.getElementById('next-btn');
    nextBtn.disabled = true;
    if(currentQuestion === questions.length - 1) {
        nextBtn.innerText = "Submit Quiz";
    }

    qData.options.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerText = opt;
        btn.onclick = () => {
            document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            nextBtn.disabled = false;
        };
        optionsContainer.appendChild(btn);
    });
}

async function submitQuiz() {
    document.getElementById('quiz-body').style.display = 'none';
    document.getElementById('quiz-footer').style.display = 'none';
    document.getElementById('quiz-header').innerHTML = '<h2>Analyzing your profile...</h2><div class="loader"></div>';
    
    const combinedAnswers = userAnswers.join(" ");

    try {
        const response = await fetch(`${API_BASE}/recommendations/quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: combinedAnswers })
        });
        const recommendations = await response.json();
        showResults(recommendations);
    } catch (error) {
        console.error("Error submitting quiz:", error);
        document.getElementById('quiz-header').innerHTML = '<h2 style="color:red;">Error fetching results</h2>';
    }
}

function showResults(courses) {
    document.getElementById('quiz-header').style.display = 'none';
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';
    
    const container = document.getElementById('recommendations-container');
    container.innerHTML = '';
    
    courses.forEach((course, index) => {
        const tagsHtml = course.tags ? course.tags.split(',').map(tag => `<span class="tag">${tag.trim()}</span>`).join('') : '';
        const delay = index * 0.1;
        
        const courseCard = document.createElement('div');
        courseCard.className = 'course-card glass-card slide-up';
        courseCard.style.animationDelay = `${delay}s`;
        
        courseCard.innerHTML = `
            <div class="course-category">${course.category}</div>
            <h3 class="course-title">${course.title}</h3>
            <p class="course-desc">${course.description}</p>
            <div class="course-tags">${tagsHtml}</div>
            <div class="course-footer">
                <a href="course.html?id=${course.id}" class="enroll-btn" style="text-decoration:none; display:inline-block; text-align:center;">View Details</a>
            </div>
        `;
        container.appendChild(courseCard);
    });
}
