"""
Long-Running Operations with Pause/Resume

Supports operations that may take extended time and need to be
pausable, resumable, and trackable.
"""

from .session_service import InterVuSessionService
from google.adk.sessions import Session
from typing import Optional, Callable, Any, Dict
import asyncio
from datetime import datetime
from .observability import logger, tracer


class LongRunningOperation:
    """
    Manager for long-running agent operations with pause/resume support.
    
    Use cases:
    - Batch interview evaluations
    - Multi-stage career workflows
    - Large-scale data processing
    """
    
    def __init__(self, session_service: InterVuSessionService):
        """
        Initialize long-running operation manager.
        
        Args:
            session_service: Session service for state persistence
        """
        self.session_service = session_service
        self.running_tasks: Dict[str, asyncio.Task] = {}
        logger.info("long_running_manager_initialized")
    
    async def start_operation(
        self,
        operation_id: str,
        user_id: str,
        task_func: Callable,
        **kwargs
    ) -> str:
        """
        Start a new long-running operation.
        
        Args:
            operation_id: Unique identifier for this operation
            user_id: User who owns this operation
            task_func: Async function to execute
            **kwargs: Arguments to pass to task_func
            
        Returns:
            Operation ID for tracking
        """
        with tracer.start_as_current_span("start_long_running_operation") as span:
            span.set_attribute("operation_id", operation_id)
            span.set_attribute("user_id", user_id)
            
            # Create session for tracking
            session = await self.session_service.create_session(
                app_name="long_running",
                user_id=user_id,
                initial_state={
                    "operation_id": operation_id,
                    "status": "running",
                    "started_at": datetime.utcnow().isoformat(),
                    "progress": 0,
                    "kwargs": kwargs
                }
            )
            
            logger.info(
                "operation_started",
                operation_id=operation_id,
                session_id=session.session_id
            )
            
            # Start task in background
            task = asyncio.create_task(
                self._run_task(session.session_id, task_func, kwargs)
            )
            self.running_tasks[operation_id] = task
            
            return operation_id
    
    async def pause_operation(self, operation_id: str):
        """
        Pause a running operation.
        
        Args:
            operation_id: Operation to pause
        """
        with tracer.start_as_current_span("pause_operation") as span:
            span.set_attribute("operation_id", operation_id)
            
            # Get session
            sessions = await self.session_service.list_user_sessions("all")
            session = next(
                (s for s in sessions if s.state.get("operation_id") == operation_id),
                None
            )
            
            if not session:
                logger.error("operation_not_found", operation_id=operation_id)
                raise ValueError(f"Operation {operation_id} not found")
            
            # Update state
            session.state["status"] = "paused"
            session.state["paused_at"] = datetime.utcnow().isoformat()
            await self.session_service.save_session(session)
            
            # Cancel task if running
            if operation_id in self.running_tasks:
                self.running_tasks[operation_id].cancel()
                del self.running_tasks[operation_id]
            
            logger.info("operation_paused", operation_id=operation_id)
    
    async def resume_operation(self, operation_id: str):
        """
        Resume a paused operation.
        
        Args:
            operation_id: Operation to resume
        """
        with tracer.start_as_current_span("resume_operation") as span:
            span.set_attribute("operation_id", operation_id)
            
            # Get session
            sessions = await self.session_service.list_user_sessions("all")
            session = next(
                (s for s in sessions if s.state.get("operation_id") == operation_id),
                None
            )
            
            if not session:
                logger.error("operation_not_found", operation_id=operation_id)
                raise ValueError(f"Operation {operation_id} not found")
            
            if session.state.get("status") != "paused":
                logger.warning(
                    "operation_not_paused",
                    operation_id=operation_id,
                    status=session.state.get("status")
                )
                return
            
            # Update state
            session.state["status"] = "running"
            session.state["resumed_at"] = datetime.utcnow().isoformat()
            await self.session_service.save_session(session)
            
            # Resume task (simplified - real implementation would restore state)
            logger.info("operation_resumed", operation_id=operation_id)
            # TODO: Restore execution state and continue
    
    async def get_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of an operation.
        
        Args:
            operation_id: Operation to check
            
        Returns:
            Status dictionary or None if not found
        """
        sessions = await self.session_service.list_user_sessions("all")
        session = next(
            (s for s in sessions if s.state.get("operation_id") == operation_id),
            None
        )
        
        if not session:
            return None
        
        return {
            "operation_id": operation_id,
            "status": session.state.get("status"),
            "progress": session.state.get("progress", 0),
            "started_at": session.state.get("started_at"),
            "paused_at": session.state.get("paused_at"),
            "completed_at": session.state.get("completed_at"),
            "error": session.state.get("error")
        }
    
    async def _run_task(
        self,
        session_id: str,
        task_func: Callable,
        kwargs: Dict
    ):
        """
        Execute the actual task with progress tracking.
        
        Args:
            session_id: Session ID for state tracking
            task_func: Function to execute
            kwargs: Function arguments
        """
        session = await self.session_service.get_session(session_id)
        
        try:
            # Execute task
            result = await task_func(**kwargs)
            
            # Mark as completed
            session.state["status"] = "completed"
            session.state["progress"] = 100
            session.state["completed_at"] = datetime.utcnow().isoformat()
            session.state["result"] = result
            await self.session_service.save_session(session)
            
            logger.info(
                "operation_completed",
                operation_id=session.state["operation_id"]
            )
            
        except asyncio.CancelledError:
            logger.info("operation_cancelled", session_id=session_id)
            
        except Exception as e:
            # Mark as failed
            session.state["status"] = "failed"
            session.state["error"] = str(e)
            session.state["failed_at"] = datetime.utcnow().isoformat()
            await self.session_service.save_session(session)
            
            logger.error(
                "operation_failed",
                operation_id=session.state["operation_id"],
                error=str(e),
                exc_info=True
            )
    
    async def cancel_operation(self, operation_id: str):
        """
        Cancel a running operation.
        
        Args:
            operation_id: Operation to cancel
        """
        if operation_id in self.running_tasks:
            self.running_tasks[operation_id].cancel()
            del self.running_tasks[operation_id]
            
            # Update session
            sessions = await self.session_service.list_user_sessions("all")
            session = next(
                (s for s in sessions if s.state.get("operation_id") == operation_id),
                None
            )
            
            if session:
                session.state["status"] = "cancelled"
                session.state["cancelled_at"] = datetime.utcnow().isoformat()
                await self.session_service.save_session(session)
            
            logger.info("operation_cancelled", operation_id=operation_id)
