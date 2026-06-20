from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Course, Enrollment, User
from recommender import get_recommendations, get_quiz_recommendations

app = Flask(__name__)
CORS(app)

import os
import shutil
import tempfile

original_db_path = os.path.join(os.path.dirname(__file__), 'database.sqlite')
db_path = os.path.join(tempfile.gettempdir(), 'database.sqlite')

if not os.path.exists(db_path):
    if os.path.exists(original_db_path):
        shutil.copy2(original_db_path, db_path)
    else:
        db_path = original_db_path
else:
    # If it exists in temp, we can just use it. 
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Dummy login user for now (from seed.py id=1)
CURRENT_USER_ID = 1

@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    courses = Course.query.all()
    result = [{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'category': c.category,
        'tags': c.tags,
        'duration': c.duration,
        'modules': c.modules.split('|') if c.modules else []
    } for c in courses]
    return jsonify(result)

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    c = Course.query.get_or_404(course_id)
    return jsonify({
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'category': c.category,
        'tags': c.tags,
        'duration': c.duration,
        'modules': c.modules.split('|') if c.modules else []
    })

@app.route('/api/recommendations', methods=['GET'])
def get_user_recommendations():
    recs = get_recommendations(CURRENT_USER_ID, num_recommendations=4)
    return jsonify(recs)

@app.route('/api/recommendations/quiz', methods=['POST'])
def quiz_recommendations():
    data = request.json
    answers_text = data.get('answers', '')
    recs = get_quiz_recommendations(answers_text, num_recommendations=4)
    return jsonify(recs)

@app.route('/api/roadmap', methods=['GET'])
def get_roadmap():
    query = request.args.get('query', '').lower().strip()
    if not query:
        query = 'technology'
        
    # Predefined roadmaps with keyword matching
    predefined = [
        {
            'domain': 'Web Development',
            'keywords': ['web', 'frontend', 'front end', 'backend', 'back end', 'full stack', 'fullstack', 'react', 'node', 'javascript', 'html'],
            'steps': [
                {'title': 'Internet Basics', 'desc': 'Understand HTTP, DNS, and Browsers.'},
                {'title': 'HTML & CSS', 'desc': 'Learn semantic HTML and responsive CSS.'},
                {'title': 'JavaScript Basics', 'desc': 'Variables, functions, DOM manipulation.'},
                {'title': 'Frontend Frameworks', 'desc': 'Learn React, Vue, or Angular.'},
                {'title': 'Backend Basics', 'desc': 'Node.js, Express, or Python/FastAPI.'},
                {'title': 'Databases', 'desc': 'SQL (PostgreSQL) and NoSQL (MongoDB).'}
            ]
        },
        {
            'domain': 'Data Science & ML',
            'keywords': ['data', 'machine learning', 'ml', 'ai', 'artificial intelligence', 'python', 'analysis', 'scientist', 'analytics'],
            'steps': [
                {'title': 'Python Programming', 'desc': 'Learn core Python logic and data structures.'},
                {'title': 'Data Manipulation', 'desc': 'Master Pandas and NumPy.'},
                {'title': 'Data Visualization', 'desc': 'Matplotlib, Seaborn, or Plotly.'},
                {'title': 'Math & Statistics', 'desc': 'Probability, distributions, hypothesis testing.'},
                {'title': 'Machine Learning', 'desc': 'Scikit-Learn: Regression, Classification.'},
                {'title': 'Deep Learning', 'desc': 'Neural Networks with PyTorch or TensorFlow.'}
            ]
        },
        {
            'domain': 'Cyber Security',
            'keywords': ['cyber', 'security', 'hack', 'ethical', 'pentest', 'network security', 'infosec'],
            'steps': [
                {'title': 'IT Fundamentals', 'desc': 'Hardware, Operating Systems, Networking.'},
                {'title': 'Networking Concepts', 'desc': 'TCP/IP, Routing, Firewalls.'},
                {'title': 'Security Basics', 'desc': 'Cryptography, Access Control, Risk.'},
                {'title': 'Ethical Hacking', 'desc': 'Penetration testing, vulnerability scanning.'},
                {'title': 'Incident Response', 'desc': 'Handling breaches and forensics.'}
            ]
        },
        {
            'domain': 'UI/UX Design',
            'keywords': ['ui', 'ux', 'design', 'figma', 'interface', 'user experience'],
            'steps': [
                {'title': 'Design Thinking', 'desc': 'Understand user needs and problem-solving.'},
                {'title': 'User Research', 'desc': 'Conduct surveys, interviews, and create personas.'},
                {'title': 'Wireframing', 'desc': 'Create low-fidelity layouts.'},
                {'title': 'Prototyping & UI', 'desc': 'Design high-fidelity interfaces using Figma.'},
                {'title': 'Testing', 'desc': 'Conduct usability tests and iterate.'}
            ]
        }
    ]
    
    matched = None
    for rm in predefined:
        if any(kw in query for kw in rm['keywords']):
            matched = {'domain': rm['domain'], 'steps': rm['steps']}
            break
            
    if not matched:
        # Dynamic fallback for ANY role typed
        formatted_query = query.title()
        matched = {
            'domain': formatted_query,
            'steps': [
                {'title': f'Introduction to {formatted_query}', 'desc': f'Understand the fundamental principles, history, and core concepts of {formatted_query}.'},
                {'title': 'Core Tools & Technologies', 'desc': 'Learn the standard software, languages, and frameworks used by industry professionals.'},
                {'title': 'Intermediate Concepts', 'desc': 'Dive deeper into complex mechanisms, architecture, and problem-solving techniques.'},
                {'title': 'Real-World Projects', 'desc': f'Apply your skills to build a strong portfolio of {formatted_query} projects.'},
                {'title': 'Advanced Specialization', 'desc': 'Focus on a niche area to become an expert and prepare for interviews.'}
            ]
        }

    return jsonify(matched)

@app.route('/api/enrollments', methods=['GET'])
def get_user_enrollments():
    enrollments = Enrollment.query.filter_by(user_id=CURRENT_USER_ID).all()
    course_ids = [e.course_id for e in enrollments]
    courses = Course.query.filter(Course.id.in_(course_ids)).all()
    result = [{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'category': c.category
    } for c in courses]
    return jsonify(result)

@app.route('/api/enroll', methods=['POST'])
def enroll_course():
    data = request.json
    course_id = data.get('course_id')
    if not course_id:
        return jsonify({'error': 'Course ID required'}), 400
        
    existing = Enrollment.query.filter_by(user_id=CURRENT_USER_ID, course_id=course_id).first()
    if existing:
        return jsonify({'message': 'Already enrolled'}), 200

    new_enrollment = Enrollment(user_id=CURRENT_USER_ID, course_id=course_id)
    db.session.add(new_enrollment)
    db.session.commit()
    
    return jsonify({'message': 'Successfully enrolled'}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
