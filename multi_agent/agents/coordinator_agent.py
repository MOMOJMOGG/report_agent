"""
Coordinator Agent for orchestrating the multi-agent retail analysis pipeline.
Manages the complete workflow: Data Fetch → Normalization → RAG → Report → Dashboard.
"""

import asyncio
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import uuid

from core.base_agent import BaseAgent, AgentConfig
from models.message_types import (
    BaseMessage, MessageType, AgentType, DateRange,
    FetchDataPayload, create_message, create_fetch_data_message
)
from config.settings import settings


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(str, Enum):
    """Pipeline execution stages."""
    INIT = "initialization"
    DATA_FETCH = "data_fetch"
    NORMALIZATION = "normalization"
    RAG_PROCESSING = "rag_processing"
    REPORT_GENERATION = "report_generation"
    DASHBOARD_READY = "dashboard_ready"
    CLEANUP = "cleanup"


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""
    # Timeout settings (in seconds)
    data_fetch_timeout: int = 300  # 5 minutes
    normalization_timeout: int = 180  # 3 minutes
    rag_processing_timeout: int = 600  # 10 minutes
    report_generation_timeout: int = 240  # 4 minutes
    total_pipeline_timeout: int = 1800  # 30 minutes
    
    # Retry settings
    max_retries_per_stage: int = 2
    retry_delay_seconds: float = 5.0
    
    # Agent coordination
    heartbeat_interval: int = 30
    status_update_interval: int = 10
    
    # Data settings
    default_date_range_days: int = 90
    max_concurrent_pipelines: int = 5


@dataclass
class PipelineExecution:
    """Tracks a single pipeline execution."""
    pipeline_id: str
    status: PipelineStatus
    current_stage: PipelineStage
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Request parameters
    date_range: DateRange = None
    tables: List[str] = None
    filters: Dict[str, Any] = None
    
    # Execution tracking
    stage_start_times: Dict[PipelineStage, datetime] = None
    stage_completion_times: Dict[PipelineStage, datetime] = None
    retry_counts: Dict[PipelineStage, int] = None
    
    # Results
    data_fetch_result: Optional[Dict[str, Any]] = None
    normalization_result: Optional[Dict[str, Any]] = None
    rag_result: Optional[Dict[str, Any]] = None
    report_result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.stage_start_times is None:
            self.stage_start_times = {}
        if self.stage_completion_times is None:
            self.stage_completion_times = {}
        if self.retry_counts is None:
            self.retry_counts = {stage: 0 for stage in PipelineStage}


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent that orchestrates the complete multi-agent pipeline.
    Manages workflow execution, error handling, and result coordination.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, pipeline_config: Optional[PipelineConfig] = None):
        # Configure for coordination operations
        agent_config = config or AgentConfig(
            max_retries=3,
            retry_delay=2.0,
            timeout_seconds=60,
            heartbeat_interval=30
        )
        
        super().__init__(AgentType.COORDINATOR, agent_config, "CoordinatorAgent")
        
        # Pipeline configuration
        self.pipeline_config = pipeline_config or PipelineConfig()
        
        # Register message handlers for all agent responses
        self.register_handler(MessageType.RAW_DATA, self.handle_raw_data)
        self.register_handler(MessageType.CLEAN_DATA, self.handle_clean_data)
        self.register_handler(MessageType.INSIGHTS, self.handle_insights)
        self.register_handler(MessageType.REPORT_READY, self.handle_report_ready)
        self.register_handler(MessageType.TASK_COMPLETED, self.handle_task_completed)
        self.register_handler(MessageType.TASK_FAILED, self.handle_task_failed)
        
        # Pipeline tracking
        self.active_pipelines: Dict[str, PipelineExecution] = {}
        self.completed_pipelines: Dict[str, PipelineExecution] = {}
        
        # Agent status tracking
        self.agent_status: Dict[AgentType, str] = {
            AgentType.DATA_FETCH: "unknown",
            AgentType.NORMALIZATION: "unknown", 
            AgentType.RAG: "unknown",
            AgentType.REPORT: "unknown",
            AgentType.DASHBOARD: "unknown"
        }
        
        # Performance metrics
        self.total_pipelines_executed = 0
        self.successful_pipelines = 0
        self.failed_pipelines = 0
        self.average_execution_time = 0.0
    
    async def _on_start(self):
        """Initialize coordinator agent."""
        self.logger.info("Coordinator agent started")
        self.logger.info(f"Max concurrent pipelines: {self.pipeline_config.max_concurrent_pipelines}")
        
        # Start monitoring task
        asyncio.create_task(self._monitoring_loop())
    
    async def _on_stop(self):
        """Cleanup coordinator agent."""
        # Cancel any active pipelines
        for pipeline_id in list(self.active_pipelines.keys()):
            await self.cancel_pipeline(pipeline_id, "System shutdown")
        
        self.logger.info(f"Coordinator agent stopped. Total pipelines: {self.total_pipelines_executed}, "
                        f"Success rate: {self.successful_pipelines/max(1, self.total_pipelines_executed)*100:.1f}%")
    
    async def start_pipeline(
        self, 
        date_range: Optional[DateRange] = None,
        tables: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new analysis pipeline.
        
        Returns:
            str: Pipeline ID for tracking
        """
        # Check concurrent pipeline limit
        if len(self.active_pipelines) >= self.pipeline_config.max_concurrent_pipelines:
            raise RuntimeError(f"Maximum concurrent pipelines ({self.pipeline_config.max_concurrent_pipelines}) reached")
        
        # Generate pipeline ID
        pipeline_id = str(uuid.uuid4())
        
        # Set defaults
        if date_range is None:
            end_date = date.today()
            start_date = end_date - timedelta(days=self.pipeline_config.default_date_range_days)
            date_range = DateRange(start=start_date, end=end_date)
        
        if tables is None:
            tables = ["returns", "warranties", "products"]
        
        if filters is None:
            filters = {"store_locations": ["all"], "product_categories": ["all"]}
        
        # Create pipeline execution tracker
        pipeline = PipelineExecution(
            pipeline_id=pipeline_id,
            status=PipelineStatus.PENDING,
            current_stage=PipelineStage.INIT,
            started_at=datetime.now(),
            date_range=date_range,
            tables=tables,
            filters=filters
        )
        
        self.active_pipelines[pipeline_id] = pipeline
        
        # Start pipeline execution
        asyncio.create_task(self._execute_pipeline(pipeline_id))
        
        self.logger.info(f"Started pipeline {pipeline_id} for date range {date_range.start} to {date_range.end}")
        return pipeline_id
    
    async def _execute_pipeline(self, pipeline_id: str):
        """Execute the complete pipeline workflow."""
        pipeline = self.active_pipelines[pipeline_id]
        
        try:
            self.logger.info(f"Executing pipeline {pipeline_id}")
            pipeline.status = PipelineStatus.RUNNING
            
            # Stage 1: Data Fetch
            await self._execute_stage(pipeline_id, PipelineStage.DATA_FETCH)
            
            # Wait for data fetch completion (handled by message handler)
            await self._wait_for_stage_completion(pipeline_id, PipelineStage.DATA_FETCH)
            
            # Stage 2: Normalization
            await self._execute_stage(pipeline_id, PipelineStage.NORMALIZATION)
            await self._wait_for_stage_completion(pipeline_id, PipelineStage.NORMALIZATION)
            
            # Stage 3: RAG Processing
            await self._execute_stage(pipeline_id, PipelineStage.RAG_PROCESSING)
            await self._wait_for_stage_completion(pipeline_id, PipelineStage.RAG_PROCESSING)
            
            # Stage 4: Report Generation
            await self._execute_stage(pipeline_id, PipelineStage.REPORT_GENERATION)
            await self._wait_for_stage_completion(pipeline_id, PipelineStage.REPORT_GENERATION)
            
            # Stage 5: Dashboard Ready
            await self._execute_stage(pipeline_id, PipelineStage.DASHBOARD_READY)
            
            # Pipeline completed successfully
            await self._complete_pipeline(pipeline_id, success=True)
            
        except Exception as e:
            self.logger.error(f"Pipeline {pipeline_id} failed: {e}")
            await self._complete_pipeline(pipeline_id, success=False, error=str(e))
    
    async def _execute_stage(self, pipeline_id: str, stage: PipelineStage):
        """Execute a specific pipeline stage."""
        pipeline = self.active_pipelines[pipeline_id]
        pipeline.current_stage = stage
        pipeline.stage_start_times[stage] = datetime.now()
        
        self.logger.info(f"Pipeline {pipeline_id}: Starting stage {stage.value}")
        
        correlation_id = f"{pipeline_id}_{stage.value}"
        
        if stage == PipelineStage.DATA_FETCH:
            # Send fetch data message
            message = create_fetch_data_message(
                AgentType.COORDINATOR,
                pipeline.date_range,
                pipeline.tables,
                pipeline.filters,
                correlation_id
            )
            await self.send_message(message)
            
        elif stage == PipelineStage.NORMALIZATION:
            # Normalization triggered by RAW_DATA message handler
            pass
            
        elif stage == PipelineStage.RAG_PROCESSING:
            # RAG processing triggered by CLEAN_DATA message handler
            pass
            
        elif stage == PipelineStage.REPORT_GENERATION:
            # Report generation triggered by INSIGHTS message handler
            pass
            
        elif stage == PipelineStage.DASHBOARD_READY:
            # Dashboard notification triggered by REPORT_READY message handler
            pass
    
    async def _wait_for_stage_completion(self, pipeline_id: str, stage: PipelineStage):
        """Wait for a pipeline stage to complete."""
        pipeline = self.active_pipelines[pipeline_id]
        timeout = self._get_stage_timeout(stage)
        
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            if stage in pipeline.stage_completion_times:
                return  # Stage completed
            
            if pipeline.status == PipelineStatus.FAILED:
                raise RuntimeError(f"Pipeline failed during stage {stage.value}")
            
            await asyncio.sleep(1)  # Check every second
        
        # Timeout occurred
        raise TimeoutError(f"Stage {stage.value} timed out after {timeout} seconds")
    
    def _get_stage_timeout(self, stage: PipelineStage) -> int:
        """Get timeout for a specific stage."""
        timeouts = {
            PipelineStage.DATA_FETCH: self.pipeline_config.data_fetch_timeout,
            PipelineStage.NORMALIZATION: self.pipeline_config.normalization_timeout,
            PipelineStage.RAG_PROCESSING: self.pipeline_config.rag_processing_timeout,
            PipelineStage.REPORT_GENERATION: self.pipeline_config.report_generation_timeout,
            PipelineStage.DASHBOARD_READY: 30  # Quick stage
        }
        return timeouts.get(stage, 60)
    
    async def _complete_pipeline(self, pipeline_id: str, success: bool, error: Optional[str] = None):
        """Complete a pipeline execution."""
        if pipeline_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[pipeline_id]
        pipeline.completed_at = datetime.now()
        
        if success:
            pipeline.status = PipelineStatus.COMPLETED
            self.successful_pipelines += 1
            self.logger.info(f"Pipeline {pipeline_id} completed successfully")
        else:
            pipeline.status = PipelineStatus.FAILED
            pipeline.error_message = error
            self.failed_pipelines += 1
            self.logger.error(f"Pipeline {pipeline_id} failed: {error}")
        
        # Move to completed pipelines
        self.completed_pipelines[pipeline_id] = pipeline
        del self.active_pipelines[pipeline_id]
        
        # Update metrics
        self.total_pipelines_executed += 1
        execution_time = (pipeline.completed_at - pipeline.started_at).total_seconds()
        self.average_execution_time = (
            (self.average_execution_time * (self.total_pipelines_executed - 1) + execution_time) /
            self.total_pipelines_executed
        )
    
    async def cancel_pipeline(self, pipeline_id: str, reason: str = "Cancelled by user"):
        """Cancel an active pipeline."""
        if pipeline_id in self.active_pipelines:
            pipeline = self.active_pipelines[pipeline_id]
            pipeline.status = PipelineStatus.CANCELLED
            pipeline.error_message = reason
            pipeline.completed_at = datetime.now()
            
            # Move to completed
            self.completed_pipelines[pipeline_id] = pipeline
            del self.active_pipelines[pipeline_id]
            
            self.logger.info(f"Pipeline {pipeline_id} cancelled: {reason}")
    
    # Message Handlers
    
    async def handle_raw_data(self, message: BaseMessage) -> BaseMessage:
        """Handle RAW_DATA from Data Fetch Agent."""
        try:
            pipeline_id = self._extract_pipeline_id(message.metadata.correlation_id)
            if not pipeline_id or pipeline_id not in self.active_pipelines:
                return None
            
            pipeline = self.active_pipelines[pipeline_id]
            pipeline.data_fetch_result = message.payload
            pipeline.stage_completion_times[PipelineStage.DATA_FETCH] = datetime.now()
            
            self.logger.info(f"Pipeline {pipeline_id}: Data fetch completed")
            
            # Forward to Normalization Agent
            response = create_message(
                MessageType.NORMALIZE_DATA,
                self.agent_type,
                AgentType.NORMALIZATION,
                message.payload,
                message.metadata.correlation_id
            )
            
            await self.send_message(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling raw data: {e}")
            raise
    
    async def handle_clean_data(self, message: BaseMessage) -> BaseMessage:
        """Handle CLEAN_DATA from Normalization Agent."""
        try:
            pipeline_id = self._extract_pipeline_id(message.metadata.correlation_id)
            if not pipeline_id or pipeline_id not in self.active_pipelines:
                return None
            
            pipeline = self.active_pipelines[pipeline_id]
            pipeline.normalization_result = message.payload
            pipeline.stage_completion_times[PipelineStage.NORMALIZATION] = datetime.now()
            
            self.logger.info(f"Pipeline {pipeline_id}: Normalization completed")
            
            # Forward to RAG Agent
            response = create_message(
                MessageType.GENERATE_INSIGHTS,
                self.agent_type,
                AgentType.RAG,
                message.payload,
                message.metadata.correlation_id
            )
            
            await self.send_message(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling clean data: {e}")
            raise
    
    async def handle_insights(self, message: BaseMessage) -> BaseMessage:
        """Handle INSIGHTS from RAG Agent."""
        try:
            pipeline_id = self._extract_pipeline_id(message.metadata.correlation_id)
            if not pipeline_id or pipeline_id not in self.active_pipelines:
                return None
            
            pipeline = self.active_pipelines[pipeline_id]
            pipeline.rag_result = message.payload
            pipeline.stage_completion_times[PipelineStage.RAG_PROCESSING] = datetime.now()
            
            self.logger.info(f"Pipeline {pipeline_id}: RAG processing completed")
            
            # Forward to Report Agent
            response = create_message(
                MessageType.CREATE_REPORT,
                self.agent_type,
                AgentType.REPORT,
                message.payload,
                message.metadata.correlation_id
            )
            
            await self.send_message(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling insights: {e}")
            raise
    
    async def handle_report_ready(self, message: BaseMessage) -> BaseMessage:
        """Handle REPORT_READY from Report Agent."""
        try:
            pipeline_id = self._extract_pipeline_id(message.metadata.correlation_id)
            if not pipeline_id or pipeline_id not in self.active_pipelines:
                return None
            
            pipeline = self.active_pipelines[pipeline_id]
            pipeline.report_result = message.payload
            pipeline.stage_completion_times[PipelineStage.REPORT_GENERATION] = datetime.now()
            pipeline.stage_completion_times[PipelineStage.DASHBOARD_READY] = datetime.now()
            
            self.logger.info(f"Pipeline {pipeline_id}: Report generation completed")
            
            # Forward to Dashboard Agent
            response = create_message(
                MessageType.DASHBOARD_READY,
                self.agent_type,
                AgentType.DASHBOARD,
                message.payload,
                message.metadata.correlation_id
            )
            
            await self.send_message(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling report ready: {e}")
            raise
    
    async def handle_task_completed(self, message: BaseMessage) -> BaseMessage:
        """Handle TASK_COMPLETED from any agent."""
        self.logger.debug(f"Task completed from {message.metadata.sender.value}")
        return None
    
    async def handle_task_failed(self, message: BaseMessage) -> BaseMessage:
        """Handle TASK_FAILED from any agent."""
        try:
            pipeline_id = self._extract_pipeline_id(message.metadata.correlation_id)
            if pipeline_id and pipeline_id in self.active_pipelines:
                error_msg = message.payload.get('error', 'Unknown error')
                await self._complete_pipeline(pipeline_id, success=False, error=error_msg)
            
            self.logger.error(f"Task failed from {message.metadata.sender.value}: {message.payload}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling task failed: {e}")
            return None
    
    def _extract_pipeline_id(self, correlation_id: Optional[str]) -> Optional[str]:
        """Extract pipeline ID from correlation ID."""
        if not correlation_id:
            return None
        
        # Correlation ID format: "pipeline_id_stage"
        parts = correlation_id.split('_')
        if len(parts) >= 1:
            return parts[0]
        return correlation_id
    
    async def _monitoring_loop(self):
        """Background monitoring loop for pipeline health."""
        while True:
            try:
                await asyncio.sleep(self.pipeline_config.status_update_interval)
                
                # Check for stuck pipelines
                current_time = datetime.now()
                for pipeline_id, pipeline in list(self.active_pipelines.items()):
                    execution_time = (current_time - pipeline.started_at).total_seconds()
                    
                    if execution_time > self.pipeline_config.total_pipeline_timeout:
                        await self._complete_pipeline(
                            pipeline_id, 
                            success=False, 
                            error=f"Pipeline timeout after {execution_time:.0f} seconds"
                        )
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    # Public API methods
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific pipeline."""
        if pipeline_id in self.active_pipelines:
            pipeline = self.active_pipelines[pipeline_id]
        elif pipeline_id in self.completed_pipelines:
            pipeline = self.completed_pipelines[pipeline_id]
        else:
            return None
        
        return {
            "pipeline_id": pipeline.pipeline_id,
            "status": pipeline.status.value,
            "current_stage": pipeline.current_stage.value,
            "started_at": pipeline.started_at.isoformat(),
            "completed_at": pipeline.completed_at.isoformat() if pipeline.completed_at else None,
            "error_message": pipeline.error_message,
            "execution_time_seconds": (
                (pipeline.completed_at or datetime.now()) - pipeline.started_at
            ).total_seconds(),
            "stage_progress": {
                stage.value: stage in pipeline.stage_completion_times
                for stage in PipelineStage
            }
        }
    
    def list_pipelines(self, status_filter: Optional[PipelineStatus] = None) -> List[Dict[str, Any]]:
        """List all pipelines with optional status filter."""
        pipelines = []
        
        # Add active pipelines
        for pipeline in self.active_pipelines.values():
            if status_filter is None or pipeline.status == status_filter:
                pipelines.append(self.get_pipeline_status(pipeline.pipeline_id))
        
        # Add completed pipelines
        for pipeline in self.completed_pipelines.values():
            if status_filter is None or pipeline.status == status_filter:
                pipelines.append(self.get_pipeline_status(pipeline.pipeline_id))
        
        # Sort by start time (newest first)
        pipelines.sort(key=lambda x: x["started_at"], reverse=True)
        return pipelines
    
    def get_coordinator_stats(self) -> Dict[str, Any]:
        """Get coordinator agent statistics."""
        return {
            "agent_type": self.agent_type.value,
            "agent_name": self.name,
            "total_pipelines": self.total_pipelines_executed,
            "successful_pipelines": self.successful_pipelines,
            "failed_pipelines": self.failed_pipelines,
            "success_rate": self.successful_pipelines / max(1, self.total_pipelines_executed),
            "average_execution_time_seconds": self.average_execution_time,
            "active_pipelines": len(self.active_pipelines),
            "max_concurrent_pipelines": self.pipeline_config.max_concurrent_pipelines,
            "agent_status": {agent.value: status for agent, status in self.agent_status.items()}
        }