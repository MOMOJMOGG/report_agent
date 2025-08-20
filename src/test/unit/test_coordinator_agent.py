"""
Unit tests for the Coordinator Agent.
Tests pipeline orchestration, message handling, workflow management, and error handling.
"""

import pytest
import asyncio
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, date, timedelta

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src" / "main" / "python"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

from agents.coordinator_agent import (
    CoordinatorAgent, PipelineConfig, PipelineExecution, 
    PipelineStatus, PipelineStage
)
from models.message_types import (
    MessageType, AgentType, DateRange, create_message
)


class TestCoordinatorAgentInit:
    """Test coordinator agent initialization."""
    
    def test_agent_initialization_default(self):
        """Test agent initialization with default config."""
        agent = CoordinatorAgent()
        
        assert agent.agent_type == AgentType.COORDINATOR
        assert agent.name == "CoordinatorAgent"
        assert MessageType.RAW_DATA in agent.message_handlers
        assert MessageType.CLEAN_DATA in agent.message_handlers
        assert MessageType.INSIGHTS in agent.message_handlers
        assert MessageType.REPORT_READY in agent.message_handlers
        assert isinstance(agent.pipeline_config, PipelineConfig)
        assert len(agent.active_pipelines) == 0
        assert len(agent.completed_pipelines) == 0
    
    def test_agent_initialization_custom_config(self):
        """Test agent initialization with custom config."""
        pipeline_config = PipelineConfig(
            max_concurrent_pipelines=3,
            data_fetch_timeout=120,
            total_pipeline_timeout=900
        )
        
        agent = CoordinatorAgent(pipeline_config=pipeline_config)
        
        assert agent.pipeline_config.max_concurrent_pipelines == 3
        assert agent.pipeline_config.data_fetch_timeout == 120
        assert agent.pipeline_config.total_pipeline_timeout == 900
    
    @pytest.mark.asyncio
    async def test_agent_startup_and_shutdown(self):
        """Test agent startup and shutdown."""
        agent = CoordinatorAgent()
        
        await agent._on_start()
        
        # Check that the agent started successfully
        assert hasattr(agent, 'active_pipelines')
        assert hasattr(agent, 'completed_pipelines')
        
        await agent._on_stop()


class TestPipelineConfig:
    """Test pipeline configuration."""
    
    def test_default_config(self):
        """Test default pipeline configuration."""
        config = PipelineConfig()
        
        assert config.data_fetch_timeout == 300
        assert config.normalization_timeout == 180
        assert config.rag_processing_timeout == 600
        assert config.report_generation_timeout == 240
        assert config.total_pipeline_timeout == 1800
        assert config.max_retries_per_stage == 2
        assert config.max_concurrent_pipelines == 5
        assert config.default_date_range_days == 90
    
    def test_custom_config(self):
        """Test custom pipeline configuration."""
        config = PipelineConfig(
            data_fetch_timeout=600,
            max_concurrent_pipelines=10,
            max_retries_per_stage=3,
            default_date_range_days=30
        )
        
        assert config.data_fetch_timeout == 600
        assert config.max_concurrent_pipelines == 10
        assert config.max_retries_per_stage == 3
        assert config.default_date_range_days == 30


class TestPipelineExecution:
    """Test pipeline execution tracking."""
    
    def test_pipeline_execution_creation(self):
        """Test pipeline execution object creation."""
        date_range = DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 3, 31)
        )
        
        execution = PipelineExecution(
            pipeline_id="test-123",
            status=PipelineStatus.PENDING,
            current_stage=PipelineStage.INIT,
            started_at=datetime.now(),
            date_range=date_range,
            tables=["returns", "warranties"],
            filters={"category": "electronics"}
        )
        
        assert execution.pipeline_id == "test-123"
        assert execution.status == PipelineStatus.PENDING
        assert execution.current_stage == PipelineStage.INIT
        assert execution.date_range == date_range
        assert execution.tables == ["returns", "warranties"]
        assert execution.filters == {"category": "electronics"}
        assert len(execution.retry_counts) == len(PipelineStage)
    
    def test_stage_tracking(self):
        """Test stage tracking functionality."""
        execution = PipelineExecution(
            pipeline_id="test-456",
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.DATA_FETCH,
            started_at=datetime.now()
        )
        
        # Track stage start
        stage_start = datetime.now()
        execution.stage_start_times[PipelineStage.DATA_FETCH] = stage_start
        
        # Track stage completion
        stage_end = datetime.now()
        execution.stage_completion_times[PipelineStage.DATA_FETCH] = stage_end
        
        assert PipelineStage.DATA_FETCH in execution.stage_start_times
        assert PipelineStage.DATA_FETCH in execution.stage_completion_times
        assert execution.stage_start_times[PipelineStage.DATA_FETCH] == stage_start
        assert execution.stage_completion_times[PipelineStage.DATA_FETCH] == stage_end


class TestPipelineManagement:
    """Test pipeline management functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return CoordinatorAgent()
    
    @pytest.mark.asyncio
    async def test_start_pipeline_success(self, agent):
        """Test successful pipeline start."""
        # Mock the _execute_pipeline method to avoid actual execution
        agent._execute_pipeline = AsyncMock()
        
        pipeline_id = await agent.start_pipeline()
        
        assert pipeline_id is not None
        assert isinstance(pipeline_id, str)
        assert pipeline_id in agent.active_pipelines
        
        pipeline = agent.active_pipelines[pipeline_id]
        assert pipeline.status == PipelineStatus.PENDING
        assert pipeline.current_stage == PipelineStage.INIT
        assert pipeline.tables == ["returns", "warranties", "products"]
    
    @pytest.mark.asyncio
    async def test_start_pipeline_with_params(self, agent):
        """Test pipeline start with custom parameters."""
        agent._execute_pipeline = AsyncMock()
        
        date_range = DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 2, 29)
        )
        tables = ["returns"]
        filters = {"category": "electronics"}
        
        pipeline_id = await agent.start_pipeline(
            date_range=date_range,
            tables=tables,
            filters=filters
        )
        
        pipeline = agent.active_pipelines[pipeline_id]
        assert pipeline.date_range == date_range
        assert pipeline.tables == tables
        assert pipeline.filters == filters
    
    @pytest.mark.asyncio
    async def test_concurrent_pipeline_limit(self, agent):
        """Test concurrent pipeline limit enforcement."""
        # Set low limit for testing
        agent.pipeline_config.max_concurrent_pipelines = 2
        agent._execute_pipeline = AsyncMock()
        
        # Start two pipelines (should succeed)
        pipeline1 = await agent.start_pipeline()
        pipeline2 = await agent.start_pipeline()
        
        assert len(agent.active_pipelines) == 2
        
        # Try to start third pipeline (should fail)
        with pytest.raises(RuntimeError, match="Maximum concurrent pipelines"):
            await agent.start_pipeline()
    
    @pytest.mark.asyncio
    async def test_cancel_pipeline(self, agent):
        """Test pipeline cancellation."""
        agent._execute_pipeline = AsyncMock()
        
        # Start pipeline
        pipeline_id = await agent.start_pipeline()
        assert pipeline_id in agent.active_pipelines
        
        # Cancel pipeline
        await agent.cancel_pipeline(pipeline_id, "Test cancellation")
        
        assert pipeline_id not in agent.active_pipelines
        assert pipeline_id in agent.completed_pipelines
        
        cancelled_pipeline = agent.completed_pipelines[pipeline_id]
        assert cancelled_pipeline.status == PipelineStatus.CANCELLED
        assert cancelled_pipeline.error_message == "Test cancellation"
    
    def test_get_pipeline_status(self, agent):
        """Test getting pipeline status."""
        # Create a mock pipeline
        pipeline = PipelineExecution(
            pipeline_id="test-789",
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.DATA_FETCH,
            started_at=datetime.now()
        )
        agent.active_pipelines["test-789"] = pipeline
        
        # Get status
        status = agent.get_pipeline_status("test-789")
        
        assert status is not None
        assert status["pipeline_id"] == "test-789"
        assert status["status"] == "running"
        assert status["current_stage"] == "data_fetch"
        assert "started_at" in status
        assert "execution_time_seconds" in status
        assert "stage_progress" in status
    
    def test_list_pipelines(self, agent):
        """Test listing pipelines."""
        # Create mock pipelines
        active_pipeline = PipelineExecution(
            pipeline_id="active-1",
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.NORMALIZATION,
            started_at=datetime.now()
        )
        
        completed_pipeline = PipelineExecution(
            pipeline_id="completed-1",
            status=PipelineStatus.COMPLETED,
            current_stage=PipelineStage.DASHBOARD_READY,
            started_at=datetime.now() - timedelta(minutes=10),
            completed_at=datetime.now()
        )
        
        agent.active_pipelines["active-1"] = active_pipeline
        agent.completed_pipelines["completed-1"] = completed_pipeline
        
        # List all pipelines
        all_pipelines = agent.list_pipelines()
        assert len(all_pipelines) == 2
        
        # Filter by status
        running_pipelines = agent.list_pipelines(PipelineStatus.RUNNING)
        assert len(running_pipelines) == 1
        assert running_pipelines[0]["pipeline_id"] == "active-1"
        
        completed_pipelines = agent.list_pipelines(PipelineStatus.COMPLETED)
        assert len(completed_pipelines) == 1
        assert completed_pipelines[0]["pipeline_id"] == "completed-1"


class TestMessageHandling:
    """Test message handling functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return CoordinatorAgent()
    
    @pytest.mark.asyncio
    async def test_handle_raw_data_success(self, agent):
        """Test successful handling of RAW_DATA message."""
        # Create a mock active pipeline
        pipeline = PipelineExecution(
            pipeline_id="test-123",
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.DATA_FETCH,
            started_at=datetime.now()
        )
        agent.active_pipelines["test-123"] = pipeline
        
        # Create test raw data message
        raw_data = {
            "returns": [{"id": 1, "reason": "defective"}],
            "warranties": [{"id": 1, "issue": "screen"}],
            "products": [{"id": "P1", "name": "Phone"}],
            "metadata": {"record_count": 3}
        }
        
        message = create_message(
            MessageType.RAW_DATA,
            AgentType.DATA_FETCH,
            AgentType.COORDINATOR,
            raw_data,
            "test-123_data_fetch"
        )
        
        # Mock send_message to capture response
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Handle message
        response = await agent.handle_raw_data(message)
        
        # Verify pipeline state updated
        assert PipelineStage.DATA_FETCH in pipeline.stage_completion_times
        assert pipeline.data_fetch_result == raw_data
        
        # Verify response message
        assert response.type == MessageType.NORMALIZE_DATA
        assert response.metadata.sender == AgentType.COORDINATOR
        assert response.metadata.recipient == AgentType.NORMALIZATION
        
        # Verify send_message was called
        assert len(sent_messages) == 1
        assert sent_messages[0].type == MessageType.NORMALIZE_DATA
    
    @pytest.mark.asyncio
    async def test_handle_clean_data_success(self, agent):
        """Test successful handling of CLEAN_DATA message."""
        # Create a mock active pipeline
        pipeline = PipelineExecution(
            pipeline_id="test-456",
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.NORMALIZATION,
            started_at=datetime.now()
        )
        agent.active_pipelines["test-456"] = pipeline
        
        # Create test clean data message
        clean_data = {
            "structured_data": {
                "returns": [{"id": "return_1", "type": "return"}],
                "warranties": [{"id": "warranty_1", "type": "warranty"}]
            },
            "embeddings_ready": True,
            "summary_stats": {"total_records": 2}
        }
        
        message = create_message(
            MessageType.CLEAN_DATA,
            AgentType.NORMALIZATION,
            AgentType.COORDINATOR,
            clean_data,
            "test-456_normalization"
        )
        
        # Mock send_message
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Handle message
        response = await agent.handle_clean_data(message)
        
        # Verify pipeline state updated
        assert PipelineStage.NORMALIZATION in pipeline.stage_completion_times
        assert pipeline.normalization_result == clean_data
        
        # Verify response message
        assert response.type == MessageType.GENERATE_INSIGHTS
        assert response.metadata.recipient == AgentType.RAG
    
    @pytest.mark.asyncio
    async def test_handle_insights_success(self, agent):
        """Test successful handling of INSIGHTS message."""
        # Create a mock active pipeline
        pipeline = PipelineExecution(
            pipeline_id="test-789",
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.RAG_PROCESSING,
            started_at=datetime.now()
        )
        agent.active_pipelines["test-789"] = pipeline
        
        # Create test insights message
        insights_data = {
            "insights": [
                {
                    "text": "Electronics have high return rate",
                    "confidence": 0.9,
                    "citations": ["return_1", "return_2"],
                    "category": "category_analysis"
                }
            ],
            "data_summaries": {"returns_stats": {"total_amount": 1000}},
            "generation_metadata": {"timestamp": datetime.now().isoformat()}
        }
        
        message = create_message(
            MessageType.INSIGHTS,
            AgentType.RAG,
            AgentType.COORDINATOR,
            insights_data,
            "test-789_rag_processing"
        )
        
        # Mock send_message
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Handle message
        response = await agent.handle_insights(message)
        
        # Verify pipeline state updated
        assert PipelineStage.RAG_PROCESSING in pipeline.stage_completion_times
        assert pipeline.rag_result == insights_data
        
        # Verify response message
        assert response.type == MessageType.CREATE_REPORT
        assert response.metadata.recipient == AgentType.REPORT
    
    @pytest.mark.asyncio
    async def test_handle_report_ready_success(self, agent):
        """Test successful handling of REPORT_READY message."""
        # Create a mock active pipeline
        pipeline = PipelineExecution(
            pipeline_id="test-101",
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.REPORT_GENERATION,
            started_at=datetime.now()
        )
        agent.active_pipelines["test-101"] = pipeline
        
        # Create test report ready message
        report_data = {
            "reports": [
                {
                    "file_path": "output/reports/analysis.xlsx",
                    "report_type": "excel_analysis",
                    "created_at": datetime.now().isoformat(),
                    "size_bytes": 9224,
                    "worksheets": ["Summary", "Details"]
                }
            ],
            "generation_metadata": {"timestamp": datetime.now().isoformat()},
            "summary_stats": {"total_reports": 1}
        }
        
        message = create_message(
            MessageType.REPORT_READY,
            AgentType.REPORT,
            AgentType.COORDINATOR,
            report_data,
            "test-101_report_generation"
        )
        
        # Mock send_message
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Handle message
        response = await agent.handle_report_ready(message)
        
        # Verify pipeline state updated
        assert PipelineStage.REPORT_GENERATION in pipeline.stage_completion_times
        assert PipelineStage.DASHBOARD_READY in pipeline.stage_completion_times
        assert pipeline.report_result == report_data
        
        # Verify response message
        assert response.type == MessageType.DASHBOARD_READY
        assert response.metadata.recipient == AgentType.DASHBOARD
    
    @pytest.mark.asyncio
    async def test_handle_task_failed(self, agent):
        """Test handling of TASK_FAILED message."""
        # Create a mock active pipeline
        pipeline = PipelineExecution(
            pipeline_id="test-fail",
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.DATA_FETCH,
            started_at=datetime.now()
        )
        agent.active_pipelines["test-fail"] = pipeline
        
        # Create test task failed message
        error_data = {
            "error": "Database connection failed",
            "stage": "data_fetch",
            "retry_count": 3
        }
        
        message = create_message(
            MessageType.TASK_FAILED,
            AgentType.DATA_FETCH,
            AgentType.COORDINATOR,
            error_data,
            "test-fail_data_fetch"
        )
        
        # Handle message
        await agent.handle_task_failed(message)
        
        # Verify pipeline moved to failed
        assert "test-fail" not in agent.active_pipelines
        assert "test-fail" in agent.completed_pipelines
        
        failed_pipeline = agent.completed_pipelines["test-fail"]
        assert failed_pipeline.status == PipelineStatus.FAILED
        assert "Database connection failed" in failed_pipeline.error_message
    
    def test_extract_pipeline_id(self, agent):
        """Test pipeline ID extraction from correlation ID."""
        # Test valid correlation ID
        assert agent._extract_pipeline_id("test-123_data_fetch") == "test-123"
        assert agent._extract_pipeline_id("pipeline-456_normalization") == "pipeline-456"
        
        # Test simple correlation ID
        assert agent._extract_pipeline_id("simple-id") == "simple-id"
        
        # Test None/empty correlation ID
        assert agent._extract_pipeline_id(None) is None
        assert agent._extract_pipeline_id("") is None


class TestStageExecution:
    """Test stage execution functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return CoordinatorAgent()
    
    @pytest.mark.asyncio
    async def test_execute_data_fetch_stage(self, agent):
        """Test data fetch stage execution."""
        # Create a mock pipeline
        pipeline_id = "test-stage-1"
        pipeline = PipelineExecution(
            pipeline_id=pipeline_id,
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.INIT,
            started_at=datetime.now(),
            date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 3, 31)),
            tables=["returns"],
            filters={"category": "all"}
        )
        agent.active_pipelines[pipeline_id] = pipeline
        
        # Mock send_message
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Execute stage
        await agent._execute_stage(pipeline_id, PipelineStage.DATA_FETCH)
        
        # Verify pipeline state updated
        assert pipeline.current_stage == PipelineStage.DATA_FETCH
        assert PipelineStage.DATA_FETCH in pipeline.stage_start_times
        
        # Verify message sent
        assert len(sent_messages) == 1
        message = sent_messages[0]
        assert message.type == MessageType.FETCH_DATA
        assert message.metadata.recipient == AgentType.DATA_FETCH
    
    def test_get_stage_timeout(self, agent):
        """Test stage timeout configuration."""
        assert agent._get_stage_timeout(PipelineStage.DATA_FETCH) == agent.pipeline_config.data_fetch_timeout
        assert agent._get_stage_timeout(PipelineStage.NORMALIZATION) == agent.pipeline_config.normalization_timeout
        assert agent._get_stage_timeout(PipelineStage.RAG_PROCESSING) == agent.pipeline_config.rag_processing_timeout
        assert agent._get_stage_timeout(PipelineStage.REPORT_GENERATION) == agent.pipeline_config.report_generation_timeout


class TestCoordinatorStatistics:
    """Test coordinator statistics and monitoring."""
    
    def test_get_coordinator_stats(self):
        """Test coordinator statistics collection."""
        agent = CoordinatorAgent()
        
        # Set some mock data
        agent.total_pipelines_executed = 10
        agent.successful_pipelines = 8
        agent.failed_pipelines = 2
        agent.average_execution_time = 150.5
        
        stats = agent.get_coordinator_stats()
        
        assert "agent_type" in stats
        assert "agent_name" in stats
        assert "total_pipelines" in stats
        assert "successful_pipelines" in stats
        assert "failed_pipelines" in stats
        assert "success_rate" in stats
        assert "average_execution_time_seconds" in stats
        assert "active_pipelines" in stats
        assert "agent_status" in stats
        
        assert stats["agent_type"] == AgentType.COORDINATOR.value
        assert stats["total_pipelines"] == 10
        assert stats["successful_pipelines"] == 8
        assert stats["failed_pipelines"] == 2
        assert stats["success_rate"] == 0.8
        assert stats["average_execution_time_seconds"] == 150.5
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_metrics(self):
        """Test metrics updates when completing pipelines."""
        agent = CoordinatorAgent()
        
        # Create mock pipeline
        pipeline_id = "metrics-test"
        pipeline = PipelineExecution(
            pipeline_id=pipeline_id,
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.REPORT_GENERATION,
            started_at=datetime.now() - timedelta(seconds=120)  # 2 minutes ago
        )
        agent.active_pipelines[pipeline_id] = pipeline
        
        # Complete pipeline successfully
        await agent._complete_pipeline(pipeline_id, success=True)
        
        # Check metrics updated
        assert agent.total_pipelines_executed == 1
        assert agent.successful_pipelines == 1
        assert agent.failed_pipelines == 0
        assert agent.average_execution_time > 0
        assert pipeline_id in agent.completed_pipelines
        assert pipeline_id not in agent.active_pipelines
        
        # Complete another pipeline with failure
        pipeline_id_2 = "metrics-test-2"
        pipeline_2 = PipelineExecution(
            pipeline_id=pipeline_id_2,
            status=PipelineStatus.RUNNING,
            current_stage=PipelineStage.DATA_FETCH,
            started_at=datetime.now() - timedelta(seconds=60)
        )
        agent.active_pipelines[pipeline_id_2] = pipeline_2
        
        await agent._complete_pipeline(pipeline_id_2, success=False, error="Test error")
        
        # Check metrics updated
        assert agent.total_pipelines_executed == 2
        assert agent.successful_pipelines == 1
        assert agent.failed_pipelines == 1


@pytest.mark.integration
class TestCoordinatorAgentIntegration:
    """Integration tests for coordinator agent."""
    
    @pytest.mark.asyncio
    async def test_full_coordination_workflow(self):
        """Test complete coordination workflow simulation."""
        agent = CoordinatorAgent()
        
        # Mock all send_message calls
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        await agent._on_start()
        
        try:
            # Start a pipeline (without actual execution)
            agent._execute_pipeline = AsyncMock()
            
            pipeline_id = await agent.start_pipeline(
                date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 3, 31)),
                tables=["returns", "warranties"],
                filters={"category": "electronics"}
            )
            
            # Verify pipeline created
            assert pipeline_id in agent.active_pipelines
            pipeline = agent.active_pipelines[pipeline_id]
            assert pipeline.status == PipelineStatus.PENDING
            
            # Simulate stage progression by handling messages
            
            # 1. Simulate data fetch completion
            raw_data_msg = create_message(
                MessageType.RAW_DATA,
                AgentType.DATA_FETCH,
                AgentType.COORDINATOR,
                {"returns": [], "warranties": [], "products": []},
                f"{pipeline_id}_data_fetch"
            )
            await agent.handle_raw_data(raw_data_msg)
            
            # 2. Simulate normalization completion
            clean_data_msg = create_message(
                MessageType.CLEAN_DATA,
                AgentType.NORMALIZATION,
                AgentType.COORDINATOR,
                {"structured_data": {}, "embeddings_ready": True, "summary_stats": {}},
                f"{pipeline_id}_normalization"
            )
            await agent.handle_clean_data(clean_data_msg)
            
            # 3. Simulate RAG completion
            insights_msg = create_message(
                MessageType.INSIGHTS,
                AgentType.RAG,
                AgentType.COORDINATOR,
                {"insights": [], "data_summaries": {}, "generation_metadata": {}},
                f"{pipeline_id}_rag_processing"
            )
            await agent.handle_insights(insights_msg)
            
            # 4. Simulate report completion
            report_msg = create_message(
                MessageType.REPORT_READY,
                AgentType.REPORT,
                AgentType.COORDINATOR,
                {"reports": [], "generation_metadata": {}, "summary_stats": {}},
                f"{pipeline_id}_report_generation"
            )
            await agent.handle_report_ready(report_msg)
            
            # Verify all stages completed
            assert PipelineStage.DATA_FETCH in pipeline.stage_completion_times
            assert PipelineStage.NORMALIZATION in pipeline.stage_completion_times
            assert PipelineStage.RAG_PROCESSING in pipeline.stage_completion_times
            assert PipelineStage.REPORT_GENERATION in pipeline.stage_completion_times
            assert PipelineStage.DASHBOARD_READY in pipeline.stage_completion_times
            
            # Verify messages were sent to appropriate agents
            assert len(sent_messages) == 4  # One for each stage
            
            # Verify message flow
            recipients = [msg.metadata.recipient for msg in sent_messages]
            assert AgentType.NORMALIZATION in recipients
            assert AgentType.RAG in recipients
            assert AgentType.REPORT in recipients
            assert AgentType.DASHBOARD in recipients
            
            # Check pipeline status
            status = agent.get_pipeline_status(pipeline_id)
            assert status is not None
            assert status["pipeline_id"] == pipeline_id
            
            # List pipelines
            pipelines = agent.list_pipelines()
            assert len(pipelines) == 1
            assert pipelines[0]["pipeline_id"] == pipeline_id
            
        finally:
            await agent._on_stop()