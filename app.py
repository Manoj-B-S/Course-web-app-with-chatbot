#!/usr/bin/env python3
"""
Iron Lady Course Management System
A web application with CRUD functionality and AI-powered features
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'iron-lady-secret-key-2024'

class CourseManager:
    def __init__(self):
        """Initialize course manager with sample data"""
        self.courses = {}
        self.feedback = []
        self.next_course_id = 1
        self.next_feedback_id = 1
        
        # Setup OpenAI
        self.openai_client = None
        self.setup_openai()
        
        # Load sample data
        self.load_sample_data()

    def setup_openai(self):
        """Setup OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=api_key)
                print("✅ OpenAI API connected for course management!")
            except Exception as e:
                print(f"⚠️ OpenAI setup failed: {e}")
                self.openai_client = None

    def load_sample_data(self):
        """Load sample courses"""
        sample_courses = [
            {
                "title": "Executive Leadership Development",
                "description": "Comprehensive 6-month program for senior executives",
                "duration": "6 months",
                "format": "Hybrid",
                "price": "₹1,50,000",
                "category": "Executive"
            },
            {
                "title": "Women in Leadership Bootcamp", 
                "description": "Intensive 3-month bootcamp for emerging women leaders",
                "duration": "3 months",
                "format": "Online",
                "price": "₹75,000",
                "category": "Leadership"
            },
            {
                "title": "Personal Branding Program",
                "description": "Build your professional brand and communication skills",
                "duration": "3 months", 
                "format": "Hybrid",
                "price": "₹50,000",
                "category": "Branding"
            }
        ]
        
        for course_data in sample_courses:
            self.add_course(course_data)

    def add_course(self, course_data: Dict) -> int:
        """Add a new course"""
        course_id = self.next_course_id
        self.courses[course_id] = {
            "id": course_id,
            "title": course_data["title"],
            "description": course_data["description"],
            "duration": course_data["duration"],
            "format": course_data["format"],
            "price": course_data["price"],
            "category": course_data["category"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.next_course_id += 1
        return course_id

    def get_course(self, course_id: int) -> Optional[Dict]:
        """Get a course by ID"""
        return self.courses.get(course_id)

    def get_all_courses(self) -> List[Dict]:
        """Get all courses"""
        return list(self.courses.values())

    def update_course(self, course_id: int, course_data: Dict) -> bool:
        """Update a course"""
        if course_id in self.courses:
            self.courses[course_id].update({
                "title": course_data["title"],
                "description": course_data["description"],
                "duration": course_data["duration"],
                "format": course_data["format"],
                "price": course_data["price"],
                "category": course_data["category"],
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return True
        return False

    def delete_course(self, course_id: int) -> bool:
        """Delete a course"""
        if course_id in self.courses:
            del self.courses[course_id]
            return True
        return False

    def add_feedback(self, feedback_data: Dict) -> int:
        """Add student feedback"""
        feedback_id = self.next_feedback_id
        feedback = {
            "id": feedback_id,
            "name": feedback_data["name"],
            "email": feedback_data["email"],
            "course": feedback_data["course"],
            "rating": int(feedback_data["rating"]),
            "feedback": feedback_data["feedback"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.feedback.append(feedback)
        self.next_feedback_id += 1
        return feedback_id

    def get_all_feedback(self) -> List[Dict]:
        """Get all feedback"""
        return self.feedback

    def generate_course_suggestions(self, category: str = "") -> List[str]:
        """AI-powered course suggestions"""
        if not self.openai_client:
            return [
                "Advanced Leadership Communication",
                "Digital Transformation for Leaders", 
                "Emotional Intelligence in Leadership",
                "Strategic Decision Making Workshop"
            ]
        
        try:
            prompt = f"""Generate 4 creative course title suggestions for Iron Lady Leadership Programs.
            Focus on women's leadership development and empowerment.
            {f'Category focus: {category}' if category else ''}
            
            Return only the course titles, one per line."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip('- ').strip() for s in suggestions if s.strip()]
            
        except Exception as e:
            print(f"AI suggestion error: {e}")
            return ["Advanced Leadership Communication", "Digital Transformation for Leaders"]

    def summarize_feedback(self) -> str:
        """AI-powered feedback summary"""
        if not self.feedback or not self.openai_client:
            return "No feedback available for summary."
        
        try:
            feedback_text = "\n".join([
                f"Rating: {f['rating']}/5 - {f['feedback']}" 
                for f in self.feedback[-10:]  # Last 10 feedback
            ])
            
            prompt = f"""Summarize the following student feedback for Iron Lady Leadership Programs.
            Provide key insights, common themes, and overall sentiment:
            
            {feedback_text}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI summary error: {e}")
            return "Unable to generate feedback summary at this time."

# Initialize course manager
course_manager = CourseManager()

# Routes
@app.route('/')
def index():
    """Home page with course overview"""
    courses = course_manager.get_all_courses()
    return render_template('index.html', courses=courses)

@app.route('/courses')
def courses():
    """Course management page"""
    courses = course_manager.get_all_courses()
    return render_template('courses.html', courses=courses)

@app.route('/course/add', methods=['GET', 'POST'])
def add_course():
    """Add new course"""
    if request.method == 'POST':
        course_data = {
            "title": request.form['title'],
            "description": request.form['description'],
            "duration": request.form['duration'],
            "format": request.form['format'],
            "price": request.form['price'],
            "category": request.form['category']
        }
        course_id = course_manager.add_course(course_data)
        flash(f'Course "{course_data["title"]}" added successfully!', 'success')
        return redirect(url_for('courses'))
    
    return render_template('add_course.html')

@app.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    """Edit existing course"""
    course = course_manager.get_course(course_id)
    if not course:
        flash('Course not found!', 'error')
        return redirect(url_for('courses'))
    
    if request.method == 'POST':
        course_data = {
            "title": request.form['title'],
            "description": request.form['description'],
            "duration": request.form['duration'],
            "format": request.form['format'],
            "price": request.form['price'],
            "category": request.form['category']
        }
        if course_manager.update_course(course_id, course_data):
            flash(f'Course "{course_data["title"]}" updated successfully!', 'success')
        else:
            flash('Failed to update course!', 'error')
        return redirect(url_for('courses'))
    
    return render_template('edit_course.html', course=course)

@app.route('/course/delete/<int:course_id>')
def delete_course(course_id):
    """Delete course"""
    course = course_manager.get_course(course_id)
    if course and course_manager.delete_course(course_id):
        flash(f'Course "{course["title"]}" deleted successfully!', 'success')
    else:
        flash('Failed to delete course!', 'error')
    return redirect(url_for('courses'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Student feedback form and display"""
    if request.method == 'POST':
        feedback_data = {
            "name": request.form['name'],
            "email": request.form['email'],
            "course": request.form['course'],
            "rating": request.form['rating'],
            "feedback": request.form['feedback']
        }
        course_manager.add_feedback(feedback_data)
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))
    
    courses = course_manager.get_all_courses()
    all_feedback = course_manager.get_all_feedback()
    return render_template('feedback.html', courses=courses, feedback=all_feedback)

@app.route('/api/suggestions')
def api_suggestions():
    """API endpoint for course suggestions"""
    category = request.args.get('category', '')
    suggestions = course_manager.generate_course_suggestions(category)
    return jsonify({"suggestions": suggestions})

@app.route('/api/feedback-summary')
def api_feedback_summary():
    """API endpoint for feedback summary"""
    summary = course_manager.summarize_feedback()
    return jsonify({"summary": summary})

@app.route('/chatbot')
def chatbot_page():
    """Chatbot interface page"""
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chatbot"""
    from chatbot import IronLadyChatbot
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    chatbot = IronLadyChatbot()
    response = chatbot.get_response(user_message)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)