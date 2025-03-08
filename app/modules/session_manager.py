import uuid


class SessionManager:
    """Manages sessions for both HOD and Teacher"""

    _sessions = {}  # user_id → {session_id, role}

    @staticmethod
    def create_session(user_id, role):
        """Creates a session for a user and stores their role (HOD/Teacher)"""
        session_id = str(uuid.uuid4())
        SessionManager._sessions[user_id] = {"session_id": session_id, "role": role}
        return session_id

    @staticmethod
    def get_session(user_id, role):
        """Retrieves the session details (session_id & role) for a user_id and role"""
        session = SessionManager._sessions.get(user_id, None)
        if session and session["role"] == role:
            return session
        return None

    @staticmethod
    def get_user_id_from_session_id(session_id, role):
        """Finds the user_id associated with a session ID and role"""
        for user_id, data in SessionManager._sessions.items():
            if data["session_id"] == session_id and data["role"] == role:
                return user_id
        return None

    @staticmethod
    def delete_session(user_id):
        """Deletes a session using user_id"""
        return SessionManager._sessions.pop(user_id, None)

    @staticmethod
    def flush_sessions():
        """Clears all sessions (logout all users)"""
        SessionManager._sessions.clear()

# -------------------- USAGE EXAMPLE --------------------
# if __name__ == "__main__":
#     hod_id = 1
#     teacher_id = 2
#
#     # Create Sessions
#     hod_session = SessionManager.create_session(hod_id, "hod")
#     teacher_session = SessionManager.create_session(teacher_id, "teacher")
#
#     print("HOD Session:", hod_session)
#     print("Teacher Session:", teacher_session)
#
#     # Retrieve Sessions
#     print("Get HOD Session:", SessionManager.get_session(hod_id, "hod"))
#     print("Get Teacher Session:", SessionManager.get_session(teacher_id, "teacher"))
#
#     # Get User By Session ID
#     print("Get User from Session:", SessionManager.get_user_id_from_session_id(hod_session))
#
#     # Delete Session
#     SessionManager.delete_session(hod_id)
#     print("HOD Session after Deletion:", SessionManager.get_session(hod_id, "hod"))
