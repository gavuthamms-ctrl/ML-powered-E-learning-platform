import os
import csv
from app import app
from models import db, User, Course, Enrollment

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create a test user
        test_user = User(username='test_learner')
        db.session.add(test_user)
        db.session.commit()

        # Load courses from CSV
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'courses.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                course = Course(
                    id=int(row['id']),
                    title=row['title'],
                    description=row['description'],
                    category=row['category'],
                    tags=row['tags'],
                    duration=row.get('duration', ''),
                    modules=row.get('modules', '')
                )
                db.session.add(course)
        
        db.session.commit()

        # Create mock enrollments for the test user to trigger ML recommendations
        # Enrolling in 'Introduction to Machine Learning' (id=1)
        enrollment = Enrollment(user_id=test_user.id, course_id=1)
        db.session.add(enrollment)
        db.session.commit()

        print("Database seeded successfully with test user and courses!")

if __name__ == '__main__':
    seed_data()
