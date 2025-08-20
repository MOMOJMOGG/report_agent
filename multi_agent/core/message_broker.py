"""
Message broker for inter-agent communication.
Handles message routing, queuing, and delivery in the multi-agent system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Set
from datetime import datetime, timedelta
from collections import defaultdict
import json

from multi_agent.models.message_types import BaseMessage, AgentType, MessageType

logger = logging.getLogger(__name__)

class MessageBroker:
    """
    Centralized message broker for agent communication.
    Handles routing, queuing, persistence, and delivery guarantees.
    """
    
    def __init__(self):
        # Agent registry: agent_type -> agent instance
        self.agents: Dict[AgentType, object] = {}
        
        # Message queues: agent_type -> list of messages
        self.message_queues: Dict[AgentType, asyncio.Queue] = defaultdict(asyncio.Queue)
        
        # Message history for debugging and auditing
        self.message_history: List[BaseMessage] = []
        
        # Subscription management: message_type -> set of agent_types
        self.subscriptions: Dict[MessageType, Set[AgentType]] = defaultdict(set)
        
        # Delivery confirmations
        self.pending_confirmations: Dict[str, BaseMessage] = {}
        
        # Broker state
        self.is_running = False
        self.stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "start_time": None
        }
        
        logger.info("Message broker initialized")
    
    async def start(self):
        """Start the message broker."""
        self.is_running = True
        self.stats["start_time"] = datetime.now()
        logger.info("Message broker started")
        
        # Start message delivery loop
        asyncio.create_task(self._delivery_loop())
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop the message broker."""
        self.is_running = False
        logger.info("Message broker stopped")
    
    def register_agent(self, agent_type: AgentType, agent_instance):
        """Register an agent with the broker."""
        self.agents[agent_type] = agent_instance
        if agent_type not in self.message_queues:
            self.message_queues[agent_type] = asyncio.Queue()
        
        logger.info(f"Registered agent: {agent_type.value}")
    
    def unregister_agent(self, agent_type: AgentType):
        """Unregister an agent from the broker."""
        if agent_type in self.agents:
            del self.agents[agent_type]
            # Keep queue for potential re-registration
            logger.info(f"Unregistered agent: {agent_type.value}")
    
    def subscribe(self, agent_type: AgentType, message_type: MessageType):
        """Subscribe an agent to a specific message type."""
        self.subscriptions[message_type].add(agent_type)
        logger.debug(f"Agent {agent_type.value} subscribed to {message_type.value}")
    
    def unsubscribe(self, agent_type: AgentType, message_type: MessageType):
        """Unsubscribe an agent from a message type."""
        self.subscriptions[message_type].discard(agent_type)
        logger.debug(f"Agent {agent_type.value} unsubscribed from {message_type.value}")
    
    async def send_message(self, message: BaseMessage) -> bool:
        """
        Send a message through the broker.
        Returns True if successfully queued, False otherwise.
        """
        try:
            # Validate message
            if not self._validate_message(message):
                return False
            
            # Store in history
            self.message_history.append(message)
            
            # Queue message for delivery
            recipient = message.metadata.recipient
            await self.message_queues[recipient].put(message)
            
            # Track pending confirmation
            self.pending_confirmations[message.metadata.message_id] = message
            
            self.stats["messages_sent"] += 1
            logger.debug(f"Queued message {message.type.value} for {recipient.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.stats["messages_failed"] += 1
            return False
    
    async def broadcast_message(self, message: BaseMessage, recipients: List[AgentType]) -> int:
        """
        Broadcast a message to multiple recipients.
        Returns number of successful sends.
        """
        success_count = 0
        
        for recipient in recipients:
            # Create copy of message with updated recipient
            broadcast_message = BaseMessage(
                type=message.type,
                metadata=message.metadata,
                payload=message.payload
            )
            broadcast_message.metadata.recipient = recipient
            
            if await self.send_message(broadcast_message):
                success_count += 1
        
        return success_count
    
    async def publish_message(self, message: BaseMessage) -> int:
        """
        Publish a message to all subscribers of the message type.
        Returns number of successful deliveries.
        """
        subscribers = self.subscriptions.get(message.type, set())
        if not subscribers:
            logger.warning(f"No subscribers for message type {message.type.value}")
            return 0
        
        return await self.broadcast_message(message, list(subscribers))
    
    async def get_messages(self, agent_type: AgentType, timeout: float = 1.0) -> List[BaseMessage]:
        """
        Get pending messages for an agent.
        Returns list of messages or empty list if timeout.
        """
        messages = []
        queue = self.message_queues[agent_type]
        
        try:
            # Get first message with timeout
            first_message = await asyncio.wait_for(queue.get(), timeout=timeout)
            messages.append(first_message)
            
            # Get any additional messages without blocking
            while not queue.empty():
                try:
                    message = queue.get_nowait()
                    messages.append(message)
                except asyncio.QueueEmpty:
                    break
            
            self.stats["messages_delivered"] += len(messages)
            
        except asyncio.TimeoutError:
            # No messages available
            pass
        
        return messages
    
    async def _delivery_loop(self):
        """Main delivery loop for processing messages."""
        while self.is_running:
            try:
                # Check for agents with pending messages
                for agent_type, agent in self.agents.items():
                    if hasattr(agent, 'receive_message'):
                        messages = await self.get_messages(agent_type, timeout=0.1)
                        
                        for message in messages:
                            try:
                                await agent.receive_message(message)
                                
                                # Confirm delivery
                                if message.metadata.message_id in self.pending_confirmations:
                                    del self.pending_confirmations[message.metadata.message_id]
                                
                                logger.debug(f"Delivered message {message.type.value} to {agent_type.value}")
                                
                            except Exception as e:
                                logger.error(f"Failed to deliver message to {agent_type.value}: {e}")
                                self.stats["messages_failed"] += 1
                
                # Brief pause to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in delivery loop: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_loop(self):
        """Cleanup loop for old messages and confirmations."""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Clean up old message history (keep last 1000 messages)
                if len(self.message_history) > 1000:
                    self.message_history = self.message_history[-1000:]
                
                # Clean up old pending confirmations (older than 5 minutes)
                cutoff_time = current_time - timedelta(minutes=5)
                expired_confirmations = [
                    msg_id for msg_id, msg in self.pending_confirmations.items()
                    if msg.metadata.timestamp < cutoff_time
                ]
                
                for msg_id in expired_confirmations:
                    del self.pending_confirmations[msg_id]
                    logger.warning(f"Expired confirmation for message {msg_id}")
                
                # Sleep for 1 minute before next cleanup
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    def _validate_message(self, message: BaseMessage) -> bool:
        """Validate message structure and content."""
        try:
            # Check required fields
            if not message.type or not message.metadata or not message.payload:
                logger.error("Message missing required fields")
                return False
            
            # Check if recipient is registered
            if message.metadata.recipient not in self.agents:
                logger.warning(f"Recipient {message.metadata.recipient.value} not registered")
                # Still allow message to be queued for future delivery
            
            return True
            
        except Exception as e:
            logger.error(f"Message validation failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, any]:
        """Get broker statistics."""
        uptime = None
        if self.stats["start_time"]:
            uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "registered_agents": len(self.agents),
            "pending_confirmations": len(self.pending_confirmations),
            "message_history_size": len(self.message_history),
            "queue_sizes": {
                agent_type.value: queue.qsize() 
                for agent_type, queue in self.message_queues.items()
            }
        }
    
    def get_message_history(
        self, 
        agent_type: Optional[AgentType] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[Dict[str, any]]:
        """Get message history with optional filtering."""
        filtered_messages = self.message_history
        
        # Apply filters
        if agent_type:
            filtered_messages = [
                msg for msg in filtered_messages 
                if msg.metadata.sender == agent_type or msg.metadata.recipient == agent_type
            ]
        
        if message_type:
            filtered_messages = [
                msg for msg in filtered_messages 
                if msg.type == message_type
            ]
        
        # Convert to dict format and limit results
        return [
            {
                "message_id": msg.metadata.message_id,
                "type": msg.type.value,
                "sender": msg.metadata.sender.value,
                "recipient": msg.metadata.recipient.value,
                "timestamp": msg.metadata.timestamp.isoformat(),
                "payload_summary": str(msg.payload)[:100] + "..." if len(str(msg.payload)) > 100 else str(msg.payload)
            }
            for msg in filtered_messages[-limit:]
        ]

# Global message broker instance
message_broker = MessageBroker()