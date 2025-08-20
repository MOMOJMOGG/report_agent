"""
Base agent class and framework for the multi-agent RAG system.
Provides common functionality for message handling, retries, and monitoring.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor
import traceback

from src.main.python.models.message_types import (
    BaseMessage, MessageType, AgentType, TaskStatusPayload, create_message
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentConfig:
    """Configuration for agent behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout_seconds: int = 300,
        heartbeat_interval: int = 30,
        max_concurrent_tasks: int = 5
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout_seconds = timeout_seconds
        self.heartbeat_interval = heartbeat_interval
        self.max_concurrent_tasks = max_concurrent_tasks

class TaskStatus:
    """Track task execution status."""
    
    def __init__(self, task_id: str, message: BaseMessage):
        self.task_id = task_id
        self.message = message
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = "running"
        self.progress = 0.0
        self.error: Optional[str] = None
        self.result: Optional[Any] = None
    
    def complete(self, result: Any = None):
        """Mark task as completed."""
        self.end_time = datetime.now()
        self.status = "completed"
        self.progress = 1.0
        self.result = result
    
    def fail(self, error: str):
        """Mark task as failed."""
        self.end_time = datetime.now()
        self.status = "failed"
        self.error = error
    
    def update_progress(self, progress: float, message: str = None):
        """Update task progress."""
        self.progress = max(0.0, min(1.0, progress))
        if message:
            logger.info(f"Task {self.task_id}: {message} ({self.progress:.1%})")

class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system."""
    
    def __init__(
        self,
        agent_type: AgentType,
        config: Optional[AgentConfig] = None,
        name: Optional[str] = None
    ):
        self.agent_type = agent_type
        self.config = config or AgentConfig()
        self.name = name or f"{agent_type.value}_agent"
        self.is_running = False
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.active_tasks: Dict[str, TaskStatus] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_tasks)
        
        # Register default message handlers
        self._register_default_handlers()
        
        # Setup logging
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.info(f"Initialized {self.name}")
    
    def _register_default_handlers(self):
        """Register default message handlers."""
        self.register_handler(MessageType.HEARTBEAT, self._handle_heartbeat)
        self.register_handler(MessageType.TASK_STARTED, self._handle_task_status)
        self.register_handler(MessageType.TASK_COMPLETED, self._handle_task_status)
        self.register_handler(MessageType.TASK_FAILED, self._handle_task_status)
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler for a specific message type."""
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for {message_type.value}")
    
    async def start(self):
        """Start the agent."""
        self.is_running = True
        self.logger.info(f"Starting {self.name}")
        
        # Start message processing loop
        asyncio.create_task(self._message_processing_loop())
        
        # Start heartbeat
        asyncio.create_task(self._heartbeat_loop())
        
        # Call agent-specific startup
        await self._on_start()
    
    async def stop(self):
        """Stop the agent."""
        self.is_running = False
        self.logger.info(f"Stopping {self.name}")
        
        # Wait for active tasks to complete
        await self._wait_for_tasks()
        
        # Cleanup
        self.executor.shutdown(wait=True)
        await self._on_stop()
    
    async def send_message(self, message: BaseMessage):
        """Send a message to another agent."""
        self.logger.debug(f"Sending message {message.type.value} to {message.metadata.recipient.value}")
        # In a real implementation, this would send to a message broker
        # For now, we'll simulate by logging
        await self._route_message(message)
    
    async def receive_message(self, message: BaseMessage):
        """Receive a message from another agent."""
        await self.message_queue.put(message)
    
    async def _message_processing_loop(self):
        """Main message processing loop."""
        while self.is_running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                # Process message
                await self._process_message(message)
                
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
                self.logger.error(traceback.format_exc())
    
    async def _process_message(self, message: BaseMessage):
        """Process a received message."""
        handler = self.message_handlers.get(message.type)
        if not handler:
            self.logger.warning(f"No handler for message type {message.type.value}")
            return
        
        task_id = f"{message.metadata.message_id}_{int(time.time())}"
        task_status = TaskStatus(task_id, message)
        self.active_tasks[task_id] = task_status
        
        try:
            self.logger.info(f"Processing message {message.type.value} from {message.metadata.sender.value}")
            
            # Execute handler with retry logic
            result = await self._execute_with_retry(handler, message, task_status)
            
            task_status.complete(result)
            self.logger.info(f"Completed processing message {message.type.value}")
            
        except Exception as e:
            error_msg = f"Failed to process message {message.type.value}: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            task_status.fail(error_msg)
            
        finally:
            # Cleanup task
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def _execute_with_retry(self, handler: Callable, message: BaseMessage, task_status: TaskStatus):
        """Execute handler with retry logic."""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self.config.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    self.logger.info(f"Retrying in {delay} seconds (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                
                # Execute handler
                if asyncio.iscoroutinefunction(handler):
                    return await handler(message)
                else:
                    # Run sync handler in executor
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(self.executor, handler, message)
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries:
                    continue
                else:
                    raise last_exception
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages."""
        while self.is_running:
            try:
                # Create heartbeat message
                heartbeat = create_message(
                    MessageType.HEARTBEAT,
                    self.agent_type,
                    AgentType.COORDINATOR,
                    {
                        "agent_name": self.name,
                        "status": "running",
                        "active_tasks": len(self.active_tasks),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                await self.send_message(heartbeat)
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _wait_for_tasks(self):
        """Wait for all active tasks to complete."""
        if not self.active_tasks:
            return
        
        self.logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete")
        
        # Wait up to timeout for tasks to complete
        start_time = time.time()
        while self.active_tasks and (time.time() - start_time) < self.config.timeout_seconds:
            await asyncio.sleep(1)
        
        if self.active_tasks:
            self.logger.warning(f"{len(self.active_tasks)} tasks did not complete within timeout")
    
    async def _route_message(self, message: BaseMessage):
        """Route message to appropriate recipient (mock implementation)."""
        # In a real system, this would use a message broker
        self.logger.info(f"Routing message {message.type.value} to {message.metadata.recipient.value}")
    
    # Default message handlers
    
    async def _handle_heartbeat(self, message: BaseMessage):
        """Handle heartbeat messages."""
        self.logger.debug("Received heartbeat")
    
    async def _handle_task_status(self, message: BaseMessage):
        """Handle task status messages."""
        payload = message.payload
        self.logger.info(f"Task status update: {payload.get('status')} for task {payload.get('task_id')}")
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    async def _on_start(self):
        """Called when agent starts."""
        pass
    
    @abstractmethod
    async def _on_stop(self):
        """Called when agent stops."""
        pass
    
    # Utility methods for subclasses
    
    def create_status_message(
        self,
        recipient: AgentType,
        task_id: str,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None
    ) -> BaseMessage:
        """Create a task status message."""
        payload = TaskStatusPayload(
            task_id=task_id,
            status=status,
            progress=progress,
            message=message,
            error=error
        )
        
        return create_message(
            MessageType.TASK_STARTED if status == "started" else
            MessageType.TASK_COMPLETED if status == "completed" else
            MessageType.TASK_FAILED,
            self.agent_type,
            recipient,
            payload
        )
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get statistics about active tasks."""
        return {
            "active_tasks": len(self.active_tasks),
            "agent_type": self.agent_type.value,
            "agent_name": self.name,
            "is_running": self.is_running,
            "uptime": datetime.now().isoformat()
        }