"""
Multi-Agent RAG System for Retail Analysis

A sophisticated AI system that orchestrates multiple specialized agents 
to process retail data and generate comprehensive reports and dashboards.
"""

__version__ = "1.0.0"
__author__ = "Generated with Claude Code"

from .core.base_agent import BaseAgent
from .core.message_broker import MessageBroker
from .models.message_types import MessageType, AgentType

__all__ = [
    "BaseAgent",
    "MessageBroker", 
    "MessageType",
    "AgentType"
]