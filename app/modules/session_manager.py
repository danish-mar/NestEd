import uuid

class SessionManager:
    """A simple in-memory session manager that stores user_id → session_id"""

    _sessions = {}  # In-memory storage (Dictionary)

    @staticmethod
    def create_session(user_id):
        """Creates a session and assigns it to a user"""
        session_id = str(uuid.uuid4())  # Generate unique session ID
        SessionManager._sessions[user_id] = session_id
        return session_id

    @staticmethod
    def get_session(user_id):
        """Retrieves the session ID for a user"""
        return SessionManager._sessions.get(user_id, None)

    @staticmethod
    def get_user_by_session(session_id):
        """Finds the user_id associated with a session ID"""
        for user_id, s_id in SessionManager._sessions.items():
            if s_id == session_id:
                return user_id
        return None

    @staticmethod
    def delete_session(user_id):
        """Deletes a session for a user"""
        return SessionManager._sessions.pop(user_id, None)

    @staticmethod
    def flush_sessions():
        """Clears all sessions (useful for logout all users)"""
        SessionManager._sessions.clear()
