import math
from models import Course, Enrollment

def tokenize(text):
    text = text.lower()
    # Remove punctuation
    for char in '.,;:"\'()[]{}-_':
        text = text.replace(char, ' ')
    return text.split()

def compute_tf(tokens):
    tf_dict = {}
    total_tokens = len(tokens)
    if total_tokens == 0:
        return tf_dict
    for token in tokens:
        tf_dict[token] = tf_dict.get(token, 0) + 1
    for token in tf_dict:
        tf_dict[token] = tf_dict[token] / float(total_tokens)
    return tf_dict

def get_recommendations(user_id, num_recommendations=4):
    courses = Course.query.all()
    if not courses:
        return []
    
    course_data = []
    for c in courses:
        combined = f"{c.title} {c.description} {c.category} {c.tags}"
        course_data.append({
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'category': c.category,
            'tags': c.tags,
            'tokens': tokenize(combined)
        })

    # Get enrollments
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    enrolled_ids = [e.course_id for e in enrollments]

    if not enrolled_ids:
        # Return first N
        return [{'id': c['id'], 'title': c['title'], 'description': c['description'], 'category': c['category'], 'tags': c['tags']} for c in course_data[:num_recommendations]]

    # Compute IDF
    doc_count = len(course_data)
    df_dict = {}
    for c in course_data:
        unique_tokens = set(c['tokens'])
        for token in unique_tokens:
            df_dict[token] = df_dict.get(token, 0) + 1
    
    idf_dict = {}
    for token, count in df_dict.items():
        idf_dict[token] = math.log10(doc_count / float(count))

    # Compute TF-IDF vectors
    for c in course_data:
        tf = compute_tf(c['tokens'])
        tfidf = {}
        for token, val in tf.items():
            tfidf[token] = val * idf_dict.get(token, 0)
        c['tfidf'] = tfidf

    def cosine_sim(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    # Calculate similarities
    sim_scores = {} # course_id -> score
    for c in course_data:
        if c['id'] in enrolled_ids:
            continue
        score = 0
        for enrolled_id in enrolled_ids:
            enrolled_c = next((x for x in course_data if x['id'] == enrolled_id), None)
            if enrolled_c:
                score += cosine_sim(c['tfidf'], enrolled_c['tfidf'])
        sim_scores[c['id']] = score
    
    # Sort
    sorted_courses = sorted([c for c in course_data if c['id'] not in enrolled_ids], key=lambda x: sim_scores[x['id']], reverse=True)

    recommendations = []
    for c in sorted_courses[:num_recommendations]:
        recommendations.append({
            'id': c['id'],
            'title': c['title'],
            'description': c['description'],
            'category': c['category'],
            'tags': c['tags']
        })

    return recommendations

def get_quiz_recommendations(quiz_text, num_recommendations=4):
    courses = Course.query.all()
    if not courses:
        return []
    
    course_data = []
    for c in courses:
        combined = f"{c.title} {c.description} {c.category} {c.tags} {c.modules}"
        course_data.append({
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'category': c.category,
            'tags': c.tags,
            'tokens': tokenize(combined)
        })

    # Compute IDF
    doc_count = len(course_data)
    df_dict = {}
    for c in course_data:
        unique_tokens = set(c['tokens'])
        for token in unique_tokens:
            df_dict[token] = df_dict.get(token, 0) + 1
    
    idf_dict = {}
    for token, count in df_dict.items():
        idf_dict[token] = math.log10(doc_count / float(count))

    # Compute TF-IDF vectors for courses
    for c in course_data:
        tf = compute_tf(c['tokens'])
        tfidf = {}
        for token, val in tf.items():
            tfidf[token] = val * idf_dict.get(token, 0)
        c['tfidf'] = tfidf

    # Vectorize Quiz Answer
    quiz_tokens = tokenize(quiz_text)
    quiz_tf = compute_tf(quiz_tokens)
    quiz_tfidf = {}
    for token, val in quiz_tf.items():
        quiz_tfidf[token] = val * idf_dict.get(token, 0)

    def cosine_sim(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    # Calculate similarities with quiz vector
    sim_scores = {}
    for c in course_data:
        sim_scores[c['id']] = cosine_sim(quiz_tfidf, c['tfidf'])
    
    # Sort
    sorted_courses = sorted(course_data, key=lambda x: sim_scores[x['id']], reverse=True)

    recommendations = []
    for c in sorted_courses[:num_recommendations]:
        recommendations.append({
            'id': c['id'],
            'title': c['title'],
            'description': c['description'],
            'category': c['category'],
            'tags': c['tags']
        })

    return recommendations
