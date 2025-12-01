"""
Session Management for InterVu using Google ADK

Provides both in-memory (development) and database-backed (production)
session services for maintaining agent context across interactions.
"""

from google.adk.sessions import InMemorySessionService, DatabaseSessionService, Session
from typing import Optional, Dict, Any
import os


class InterVuSessionService:
    """
    Unified session service for InterVu agents.
    
    Handles session creation, retrieval, and persistence across
    interview sessions, career workflows, and user interactions.
    """
    
    def __init__(self, use_db: bool = False):
        """
        Initialize session service.
        
        Args:
            use_db: If True, use DatabaseSessionService with PostgreSQL.
                   If False, use InMemorySessionService for development.
        """
        if use_db:
            # Production: Use PostgreSQL for persistence
            connection_string = os.getenv(
                "DATABASE_URL",
                "postgresql://localhost:5432/intervu_sessions"
            )
            self.service = DatabaseSessionService(
                connection_string=connection_string
            )
        else:
            # Development: Use in-memory storage  
            self.service = InMemorySessionService()
        
        self.use_db = use_db
    
    async def create_session(
        self,
        app_name: str,
        user_id: str,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new session for a user interaction.
        
        Args:
            app_name: Application name (e.g., "interview", "career_tools")
            user_id: User ID from authentication
            initial_state: Optional initial state dictionary
            
        Returns:
            Created Session object
        """
        session = await self.service.create_session(
            app_name=app_name,
            user_id=user_id
        )
        
        if initial_state:
            for key, value in initial_state.items():
                session.state[key] = value
            await self.save_session(session)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve an existing session by ID.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session object if found, None otherwise
        """
        return await self.service.get_session(session_id)
    
    async def save_session(self, session: Session):
        """
        Save session state and events.
        
        Args:
            session: Session object to persist
        """
        await self.service.save_session(session)
    
    async def delete_session(self, session_id: str):
        """
        Delete a session.
        
        Args:
            session_id: Session to delete
        """
        if hasattr(self.service, 'delete_session'):
            await self.service.delete_session(session_id)
    
    async def list_user_sessions(self, user_id: str) -> list[Session]:
        """
        Get all sessions for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Session objects
        """
        if hasattr(self.service, 'list_sessions'):
            return await self.service.list_sessions(user_id=user_id)
        return []
    
    def create_persistent_state_key(self, key: str, scope: str = "user") -> str:
        """
        Create a magic state key for persistence across sessions.
        
        ADK supports special prefixes:
        - user: - Persists across all sessions for a user
        - app: - Persists across all sessions for an app
        
        Args:
            key: State key name
            scope: Either "user" or "app"
            
        Returns:
            Prefixed key for persistent state
        """
        if scope not in ["user", "app"]:
            raise ValueError("Scope must be 'user' or 'app'")
        return f"{scope}:{key}"


# Singleton instance
_session_service: Optional[InterVuSessionService] = None


def get_session_service(use_db: bool = False) -> InterVuSessionService:
    """
    Get or create the global session service instance.
    
    Args:
        use_db: Whether to use database backend
        
    Returns:
        Shared InterVuSessionService instance
    """
    global _session_service
    if _session_service is None:
        _session_service = InterVuSessionService(use_db=use_db)
    return _session_service
