import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from ..models.complaint import Complaint
from ..models.user import User
from typing import List, Optional

class ChatbotService:
    def __init__(self):
        # Ensure environment is loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                print("[OK] Chatbot Service: Gemini 2.5 Flash Initialized")
            except Exception as e:
                print(f"[ERROR] Chatbot Service Init Failed: {e}")
        else:
            print("[WARNING] Chatbot Service: No GEMINI_API_KEY found")

    def get_user_context(self, db: Session, user_id: int, role: str, area: Optional[str] = None) -> str:
        """Fetch relevant complaint data for context."""
        try:
            from sqlalchemy.orm import joinedload
            query = db.query(Complaint).options(joinedload(Complaint.reporter_user))
            
            if role == "admin":
                complaints = query.order_by(Complaint.created_at.desc()).limit(20).all()
            elif role == "area_admin":
                complaints = query.filter(Complaint.area == area).order_by(Complaint.created_at.desc()).limit(15).all()
            else:
                complaints = query.filter(Complaint.user_id == user_id).order_by(Complaint.created_at.desc()).limit(10).all()

            if not complaints:
                return "The system has no complaints recorded yet."

            context = "Here are the relevant complaints with reporter details:\n"
            for c in complaints:
                desc = (c.description or "No description provided")[:100]
                reporter = c.reporter_user.username if c.reporter_user else f"Anonymous (UID:{c.user_id})"
                context += f"- ID: {c.id}, Reporter Username: {reporter}, Category: {c.category or 'General'}, Status: {c.status or 'SUBMITTED'}, Priority: {c.priority or 'MEDIUM'}, Description: {desc}\n"
            
            return context
        except Exception as e:
            import traceback
            traceback.print_exc()
            return "Error retrieving complaint history context."

    async def get_response(self, db: Session, user: User, message: str) -> str:
        if not self.model:
            return "Chatbot is currently unavailable due to missing API key."

        context = self.get_user_context(db, user.id, user.role, user.area)
        
        system_prompt = f"""
        You are 'CivicAssist', an AI chatbot for the Civic Issue Management System of Chennai.
        You assist users (Citizens, Admins, and Area Admins).
        Current User Role: {user.role}
        Current User Area: {user.area or 'All Chennai'}
        
        User Context from Database:
        {context}
        
        Guidelines:
        1. Answer correctly based on the context provided.
        2. If a citizen asks about their complaint, refer to the IDs in the context if they match.
        3. If an admin asks for a summary, provide one based on the context.
        4. Be polite, professional, and helpful.
        5. If you don't know the answer, say you don't know but mention that the civic body is working on it.
        6. Keep responses concise and focused on civic issues.
        7. Use the complaint statuses (SUBMITTED, IN_PROGRESS, RESOLVED) to explain progress.
        """

        try:
            # Using generate_content instead of chat for simpler stateless requests if history isn't maintained
            full_prompt = f"{system_prompt}\n\nUser Question: {message}"
            # Use the async version of the model call
            response = await self.model.generate_content_async(full_prompt)
            return response.text
        except Exception as e:
            import traceback
            print("--- Chatbot Service Error ---")
            traceback.print_exc()
            print("------------------------------")
            return f"I'm having trouble connecting to my brain right now ({str(e)}). Please try again later."

chatbot_service = ChatbotService()
