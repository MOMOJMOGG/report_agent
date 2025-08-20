"""
Message types and contracts for multi-agent communication.
Defines the JSON message formats for agent-to-agent communication.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import date, datetime
from enum import Enum
import json

class MessageType(str, Enum):
    """Enumeration of message types used in the multi-agent system."""
    
    # Coordinator messages
    FETCH_DATA = "FETCH_DATA"
    NORMALIZE_DATA = "NORMALIZE_DATA"
    GENERATE_INSIGHTS = "GENERATE_INSIGHTS"
    CREATE_REPORT = "CREATE_REPORT"
    CREATE_DASHBOARD = "CREATE_DASHBOARD"
    
    # Data flow messages
    RAW_DATA = "RAW_DATA"
    CLEAN_DATA = "CLEAN_DATA"
    INSIGHTS = "INSIGHTS"
    REPORT_READY = "REPORT_READY"
    DASHBOARD_READY = "DASHBOARD_READY"
    
    # Status messages
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    HEARTBEAT = "HEARTBEAT"

class AgentType(str, Enum):
    """Types of agents in the system."""
    COORDINATOR = "coordinator"
    DATA_FETCH = "data_fetch"
    NORMALIZATION = "normalization"
    RAG = "rag"
    REPORT = "report"
    DASHBOARD = "dashboard"

@dataclass
class DateRange:
    """Date range specification."""
    start: date
    end: date
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'DateRange':
        return cls(
            start=datetime.fromisoformat(data["start"]).date(),
            end=datetime.fromisoformat(data["end"]).date()
        )

@dataclass
class MessageMetadata:
    """Message metadata for tracking and routing."""
    message_id: str
    sender: AgentType
    recipient: AgentType
    timestamp: datetime
    correlation_id: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender.value,
            "recipient": self.recipient.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count
        }

@dataclass
class BaseMessage:
    """Base message structure for all agent communications."""
    type: MessageType
    metadata: MessageMetadata
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        """Serialize message to JSON."""
        data = {
            "type": self.type.value,
            "metadata": self.metadata.to_dict(),
            "payload": self.payload
        }
        return json.dumps(data, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseMessage':
        """Deserialize message from JSON."""
        data = json.loads(json_str)
        metadata = MessageMetadata(
            message_id=data["metadata"]["message_id"],
            sender=AgentType(data["metadata"]["sender"]),
            recipient=AgentType(data["metadata"]["recipient"]),
            timestamp=datetime.fromisoformat(data["metadata"]["timestamp"]),
            correlation_id=data["metadata"].get("correlation_id"),
            retry_count=data["metadata"].get("retry_count", 0)
        )
        return cls(
            type=MessageType(data["type"]),
            metadata=metadata,
            payload=data["payload"]
        )

# Specific message payload types

@dataclass
class FetchDataPayload:
    """Payload for FETCH_DATA message."""
    date_range: DateRange
    tables: List[str]
    filters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date_range": self.date_range.to_dict(),
            "tables": self.tables,
            "filters": self.filters
        }

@dataclass
class RawDataPayload:
    """Payload for RAW_DATA message."""
    returns: List[Dict[str, Any]]
    warranties: List[Dict[str, Any]]
    products: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "returns": self.returns,
            "warranties": self.warranties,
            "products": self.products,
            "metadata": self.metadata
        }

@dataclass
class CleanDataPayload:
    """Payload for CLEAN_DATA message."""
    structured_data: Dict[str, Any]
    embeddings_ready: bool
    summary_stats: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "structured_data": self.structured_data,
            "embeddings_ready": self.embeddings_ready,
            "summary_stats": self.summary_stats
        }

@dataclass
class InsightData:
    """Individual insight with citations."""
    text: str
    confidence: float
    citations: List[str]
    category: str
    importance: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class InsightsPayload:
    """Payload for INSIGHTS message."""
    insights: List[InsightData]
    data_summaries: Dict[str, Any]
    generation_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "insights": [insight.to_dict() for insight in self.insights],
            "data_summaries": self.data_summaries,
            "generation_metadata": self.generation_metadata
        }

@dataclass
class ReportData:
    """Individual report file with metadata."""
    file_path: str
    report_type: str
    created_at: datetime
    size_bytes: int
    worksheets: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "report_type": self.report_type,
            "created_at": self.created_at.isoformat(),
            "size_bytes": self.size_bytes,
            "worksheets": self.worksheets
        }

@dataclass
class ReportReadyPayload:
    """Payload for REPORT_READY message."""
    reports: List[ReportData]
    generation_metadata: Dict[str, Any]
    summary_stats: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reports": [report.to_dict() for report in self.reports],
            "generation_metadata": self.generation_metadata,
            "summary_stats": self.summary_stats
        }

@dataclass
class TaskStatusPayload:
    """Payload for task status messages."""
    task_id: str
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# Message factory functions

def create_message(
    msg_type: MessageType,
    sender: AgentType,
    recipient: AgentType,
    payload: Union[Dict[str, Any], Any],
    correlation_id: Optional[str] = None
) -> BaseMessage:
    """Create a properly formatted message."""
    from uuid import uuid4
    
    metadata = MessageMetadata(
        message_id=str(uuid4()),
        sender=sender,
        recipient=recipient,
        timestamp=datetime.now(),
        correlation_id=correlation_id
    )
    
    # Convert payload to dict if it's a dataclass
    if hasattr(payload, 'to_dict'):
        payload_dict = payload.to_dict()
    elif isinstance(payload, dict):
        payload_dict = payload
    else:
        payload_dict = asdict(payload) if hasattr(payload, '__dataclass_fields__') else {"data": payload}
    
    return BaseMessage(
        type=msg_type,
        metadata=metadata,
        payload=payload_dict
    )

def create_fetch_data_message(
    sender: AgentType,
    date_range: DateRange,
    tables: List[str] = None,
    filters: Dict[str, Any] = None,
    correlation_id: Optional[str] = None
) -> BaseMessage:
    """Create a FETCH_DATA message."""
    payload = FetchDataPayload(
        date_range=date_range,
        tables=tables or ["returns", "warranties", "products"],
        filters=filters or {"store_locations": ["all"], "product_categories": ["all"]}
    )
    return create_message(
        MessageType.FETCH_DATA,
        sender,
        AgentType.DATA_FETCH,
        payload,
        correlation_id
    )

def create_insights_message(
    sender: AgentType,
    recipient: AgentType,
    insights: List[InsightData],
    data_summaries: Dict[str, Any],
    generation_metadata: Dict[str, Any] = None,
    correlation_id: Optional[str] = None
) -> BaseMessage:
    """Create an INSIGHTS message."""
    payload = InsightsPayload(
        insights=insights,
        data_summaries=data_summaries,
        generation_metadata=generation_metadata or {}
    )
    return create_message(
        MessageType.INSIGHTS,
        sender,
        recipient,
        payload,
        correlation_id
    )