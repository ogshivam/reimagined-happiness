"""
Session Manager for Streamlit App
Handles persistent state across reruns and page refreshes
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import streamlit as st

class SessionManager:
    """Manages session persistence for Streamlit app"""
    
    def __init__(self, session_dir: str = "temp_sessions"):
        self.session_dir = session_dir
        self.ensure_session_dir()
    
    def ensure_session_dir(self):
        """Create session directory if it doesn't exist"""
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)
    
    def get_session_file(self, session_id: str) -> str:
        """Get the file path for a session"""
        return os.path.join(self.session_dir, f"{session_id}.json")
    
    def save_session(self, session_id: str, conversation_history: List[Dict], metadata: Dict = None):
        """Save session data to file"""
        try:
            session_data = {
                "session_id": session_id,
                "conversation_history": conversation_history,
                "metadata": metadata or {},
                "last_updated": datetime.now().isoformat(),
                "created": metadata.get("created", datetime.now().isoformat()) if metadata else datetime.now().isoformat()
            }
            
            session_file = self.get_session_file(session_id)
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            st.error(f"Failed to save session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """Load session data from file"""
        try:
            session_file = self.get_session_file(session_id)
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            st.error(f"Failed to load session: {e}")
            return None
    
    def list_sessions(self) -> List[Dict]:
        """List all available sessions"""
        sessions = []
        try:
            for file in os.listdir(self.session_dir):
                if file.endswith('.json'):
                    session_id = file.replace('.json', '')
                    session_data = self.load_session(session_id)
                    if session_data:
                        sessions.append({
                            "session_id": session_id,
                            "last_updated": session_data.get("last_updated"),
                            "message_count": len(session_data.get("conversation_history", [])),
                            "created": session_data.get("created")
                        })
        except Exception as e:
            st.error(f"Failed to list sessions: {e}")
        
        return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session file"""
        try:
            session_file = self.get_session_file(session_id)
            if os.path.exists(session_file):
                os.remove(session_file)
                return True
            return False
        except Exception as e:
            st.error(f"Failed to delete session: {e}")
            return False
    
    def cleanup_old_sessions(self, days_old: int = 7):
        """Clean up sessions older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for file in os.listdir(self.session_dir):
                if file.endswith('.json'):
                    session_id = file.replace('.json', '')
                    session_data = self.load_session(session_id)
                    
                    if session_data:
                        last_updated = datetime.fromisoformat(session_data.get("last_updated", "1970-01-01"))
                        if last_updated < cutoff_date:
                            self.delete_session(session_id)
                            cleaned_count += 1
            
            return cleaned_count
        except Exception as e:
            st.error(f"Failed to cleanup sessions: {e}")
            return 0

# Global session manager instance
session_manager = SessionManager()

def auto_save_session():
    """Auto-save current session state"""
    if 'session_id' in st.session_state and st.session_state.session_id:
        if 'conversation_history' in st.session_state:
            session_manager.save_session(
                st.session_state.session_id,
                st.session_state.conversation_history,
                {"auto_saved": True, "url": dict(st.query_params)}
            )

def restore_session_if_exists():
    """Restore session if it exists in URL params or state"""
    query_params = st.query_params
    
    # Check if session_id in URL
    if 'session' in query_params:
        session_id = query_params['session']
        session_data = session_manager.load_session(session_id)
        
        if session_data:
            st.session_state.session_id = session_id
            st.session_state.conversation_history = session_data.get("conversation_history", [])
            return True
    
    return False 