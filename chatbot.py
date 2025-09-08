#!/usr/bin/env python3
"""
Iron Lady Leadership Programs Chatbot
A simple FAQ chatbot with AI-powered enhancements using OpenAI API
"""

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class IronLadyChatbot:
    def __init__(self):
        """Initialize the chatbot with FAQ data and OpenAI client"""
        self.openai_client = None
        self.setup_openai()
        
        # Iron Lady FAQ Database
        self.faq_data = {
            "programs": {
                "question": "What programs does Iron Lady offer?",
                "answer": """Iron Lady offers comprehensive leadership programs including:
                
• Executive Leadership Development Program (6 months)
• Women in Leadership Bootcamp (3 months)
• Corporate Mentorship Program (4 months)
• Leadership Skills Workshop Series (2 months)
• Personal Branding & Communication Program (3 months)
• Strategic Thinking & Decision Making Course (2 months)

All programs are designed to empower women leaders across various industries."""
            },
            "duration": {
                "question": "What is the program duration?",
                "answer": """Program durations vary based on the course:

• Executive Leadership Development: 6 months
• Women in Leadership Bootcamp: 3 months
• Corporate Mentorship Program: 4 months
• Leadership Skills Workshop: 2 months
• Personal Branding Program: 3 months
• Strategic Thinking Course: 2 months

Each program includes weekly sessions, practical assignments, and one-on-one mentoring."""
            },
            "format": {
                "question": "Is the program online or offline?",
                "answer": """Iron Lady offers flexible learning formats:

• Hybrid Model: Combination of online and offline sessions
• Online Sessions: Live interactive webinars, recorded lectures, virtual group discussions
• Offline Sessions: In-person workshops, networking events, practical exercises
• Location: Physical sessions conducted at ITPL, Bengaluru
• Flexibility: 70% online, 30% offline for maximum convenience

All sessions are recorded for later review."""
            },
            "certificates": {
                "question": "Are certificates provided?",
                "answer": """Yes! Iron Lady provides comprehensive certification:

• Official Certificate of Completion for all programs
• Digital badges for LinkedIn profiles
• Industry-recognized credentials
• Continuing Education Units (CEUs) where applicable
• Portfolio of completed projects and case studies
• Letter of recommendation from mentors (upon request)

Certificates are issued upon successful completion of all program requirements."""
            },
            "mentors": {
                "question": "Who are the mentors/coaches?",
                "answer": """Our expert mentor team includes:

• Senior executives from Fortune 500 companies
• Successful women entrepreneurs and founders
• Industry leaders with 15+ years of experience
• Certified leadership coaches and consultants
• Former C-suite executives from various sectors
• International speakers and thought leaders

Mentor-to-participant ratio is maintained at 1:8 for personalized attention.
Each participant is assigned a dedicated mentor based on their career goals."""
            }
        }
        
        # Keywords for intent recognition
        self.keywords = {
            "programs": ["program", "course", "offer", "available", "what", "services"],
            "duration": ["duration", "time", "long", "period", "months", "weeks"],
            "format": ["online", "offline", "mode", "format", "where", "location"],
            "certificates": ["certificate", "certification", "credential", "badge"],
            "mentors": ["mentor", "coach", "teacher", "instructor", "guide", "expert"]
        }

    def setup_openai(self):
        """Setup OpenAI client if API key is available"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=api_key)
                print("✅ OpenAI API connected successfully!")
            except Exception as e:
                print(f"⚠️ OpenAI setup failed: {e}")
                self.openai_client = None
        else:
            print("⚠️ No OpenAI API key found. Using basic FAQ responses only.")

    def find_intent(self, user_input: str) -> Optional[str]:
        """Find the most likely intent based on keywords"""
        user_input_lower = user_input.lower()
        
        # Direct keyword matching
        for intent, keywords in self.keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return intent
        
        return None

    def get_faq_response(self, intent: str) -> str:
        """Get FAQ response for a given intent"""
        if intent in self.faq_data:
            return self.faq_data[intent]["answer"]
        return None

    def get_ai_response(self, user_input: str, context: str = "") -> Optional[str]:
        """Get AI-powered response using OpenAI"""
        if not self.openai_client:
            return None
        
        try:
            system_prompt = """You are a helpful assistant for Iron Lady Leadership Programs. 
            You should provide accurate, encouraging, and professional responses about leadership development.
            Keep responses concise but informative. Always maintain a supportive and empowering tone.
            
            Available Programs Context:
            - Executive Leadership Development (6 months)
            - Women in Leadership Bootcamp (3 months) 
            - Corporate Mentorship Program (4 months)
            - Leadership Skills Workshop (2 months)
            - Personal Branding Program (3 months)
            - Strategic Thinking Course (2 months)
            
            All programs are hybrid (70% online, 30% offline) with expert mentors and certificates provided."""
            
            if context:
                system_prompt += f"\n\nRelevant FAQ Context: {context}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"AI response error: {e}")
            return None

    def get_response(self, user_input: str) -> str:
        """Main method to get chatbot response"""
        if not user_input.strip():
            return "Please ask me something about Iron Lady's leadership programs!"
        
        # Find intent
        intent = self.find_intent(user_input)
        
        # Get FAQ response if intent found
        faq_response = None
        if intent:
            faq_response = self.get_faq_response(intent)
        
        # Try AI response for more natural interaction
        ai_response = self.get_ai_response(user_input, faq_response or "")
        
        # Return AI response if available, otherwise FAQ response
        if ai_response:
            return ai_response
        elif faq_response:
            return faq_response
        else:
            return """I'd be happy to help you learn about Iron Lady's leadership programs! 

You can ask me about:
• What programs are offered
• Program duration and format
• Online/offline availability  
• Certification details
• Our mentors and coaches

What would you like to know?"""

    def run_console_chat(self):
        """Run the chatbot in console mode"""
        print("🌟 Welcome to Iron Lady Leadership Programs Chatbot! 🌟")
        print("Ask me anything about our leadership development programs.")
        print("Type 'quit', 'exit', or 'bye' to end the conversation.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("Chatbot: Thank you for your interest in Iron Lady! Have a great day! 👋")
                    break
                
                response = self.get_response(user_input)
                print(f"Chatbot: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nChatbot: Goodbye! Feel free to come back anytime! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function to run the chatbot"""
    chatbot = IronLadyChatbot()
    chatbot.run_console_chat()

if __name__ == "__main__":
    main()