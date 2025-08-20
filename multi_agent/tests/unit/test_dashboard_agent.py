"""
Unit tests for the Dashboard Agent.
Tests FastAPI endpoints, job management, file handling, and API responses.
"""

import pytest
import asyncio
import tempfile
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
# Simplified path structure
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

from agents.dashboard_agent import DashboardAgent, DashboardConfig, AnalysisRequest
from models.message_types import (
    MessageType, AgentType, ReportData, ReportReadyPayload, create_message
)


class TestDashboardAgentInit:
    """Test dashboard agent initialization."""
    
    def test_agent_initialization_default(self):
        """Test agent initialization with default config."""
        agent = DashboardAgent()
        
        assert agent.agent_type == AgentType.DASHBOARD
        assert agent.name == "DashboardAgent"
        assert MessageType.REPORT_READY in agent.message_handlers
        assert isinstance(agent.dashboard_config, DashboardConfig)
        assert len(agent.active_jobs) == 0
        assert len(agent.completed_jobs) == 0
        assert agent.app is not None
    
    def test_agent_initialization_custom_config(self):
        """Test agent initialization with custom config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dashboard_config = DashboardConfig(
                host="0.0.0.0",
                port=9000,
                debug=True,
                static_files_path=temp_dir
            )
            
            agent = DashboardAgent(dashboard_config=dashboard_config)
            
            assert agent.dashboard_config.host == "0.0.0.0"
            assert agent.dashboard_config.port == 9000
            assert agent.dashboard_config.debug is True
            assert agent.dashboard_config.static_files_path == temp_dir
    
    @pytest.mark.asyncio
    async def test_agent_startup_and_shutdown(self):
        """Test agent startup and shutdown."""
        agent = DashboardAgent()
        
        await agent._on_start()
        
        # Check that the agent started successfully
        assert hasattr(agent, 'app')
        
        await agent._on_stop()


class TestDashboardConfig:
    """Test dashboard configuration."""
    
    def test_default_config(self):
        """Test default dashboard configuration."""
        config = DashboardConfig()
        
        assert config.host == "127.0.0.1"
        assert config.port == 8000
        assert config.debug is False
        assert config.max_file_size_mb == 10
        assert "http://localhost:3000" in config.cors_origins
    
    def test_custom_config(self):
        """Test custom dashboard configuration."""
        config = DashboardConfig(
            host="0.0.0.0",
            port=9000,
            debug=True,
            cors_origins=["http://example.com"],
            max_file_size_mb=20
        )
        
        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.debug is True
        assert config.cors_origins == ["http://example.com"]
        assert config.max_file_size_mb == 20


class TestAPIEndpoints:
    """Test FastAPI endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        agent = DashboardAgent()
        return TestClient(agent.app)
    
    @pytest.fixture
    def agent_with_client(self):
        """Create agent and client for testing."""
        agent = DashboardAgent()
        client = TestClient(agent.app)
        return agent, client
    
    def test_root_endpoint(self, client):
        """Test root API endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Retail Analysis Dashboard API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "endpoints" in data
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "active_jobs" in data
        assert "completed_jobs" in data
    
    def test_start_analysis_endpoint(self, client):
        """Test start analysis endpoint."""
        request_data = {
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-03-31",
            "tables": ["returns", "warranties"],
            "filters": {"category": "electronics"}
        }
        
        response = client.post("/api/v1/analysis/start", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "started"
        assert isinstance(data["job_id"], str)
    
    def test_list_jobs_endpoint(self, agent_with_client):
        """Test list jobs endpoint."""
        agent, client = agent_with_client
        
        # Initially should have no jobs
        response = client.get("/api/v1/analysis/jobs")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert len(data["jobs"]) == 0
        
        # Start a job
        request_data = {
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-03-31"
        }
        
        start_response = client.post("/api/v1/analysis/start", json=request_data)
        job_id = start_response.json()["job_id"]
        
        # Now should have one job
        response = client.get("/api/v1/analysis/jobs")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["jobs"]) == 1
        assert data["jobs"][0]["job_id"] == job_id
    
    def test_get_job_status_endpoint(self, agent_with_client):
        """Test get job status endpoint."""
        agent, client = agent_with_client
        
        # Test non-existent job
        response = client.get("/api/v1/analysis/nonexistent/status")
        assert response.status_code == 404
        
        # Start a job
        request_data = {
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-03-31"
        }
        
        start_response = client.post("/api/v1/analysis/start", json=request_data)
        job_id = start_response.json()["job_id"]
        
        # Get job status
        response = client.get(f"/api/v1/analysis/{job_id}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] in ["pending", "running"]
        assert 0 <= data["progress"] <= 1
    
    def test_list_reports_endpoint(self, client):
        """Test list reports endpoint."""
        response = client.get("/api/v1/reports")
        assert response.status_code == 200
        
        data = response.json()
        assert "reports" in data
        assert isinstance(data["reports"], list)
    
    def test_download_report_endpoint(self, client):
        """Test download report endpoint for non-existent file."""
        response = client.get("/api/v1/reports/nonexistent.xlsx/download")
        assert response.status_code == 404
    
    def test_upload_file_endpoint(self, client):
        """Test file upload endpoint."""
        # Test file upload
        test_content = b"test,data,content\n1,2,3\n4,5,6"
        
        response = client.post(
            "/api/v1/data/upload",
            files={"file": ("test.csv", test_content, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.csv"
        assert data["size"] == len(test_content)
        assert "saved_path" in data


class TestJobManagement:
    """Test job management functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return DashboardAgent()
    
    @pytest.mark.asyncio
    async def test_job_lifecycle(self, agent):
        """Test complete job lifecycle."""
        request = AnalysisRequest(
            date_range_start="2024-01-01",
            date_range_end="2024-03-31",
            tables=["returns", "warranties"],
            filters={"category": "electronics"}
        )
        
        # Start analysis pipeline
        job_id = "test-job-123"
        
        # Mock the pipeline execution
        with patch.object(agent, '_run_analysis_pipeline') as mock_pipeline:
            mock_pipeline.return_value = None
            
            # Simulate starting a job
            from multi_agent.agents.dashboard_agent import AnalysisStatus
            job_status = AnalysisStatus(
                job_id=job_id,
                status="pending",
                progress=0.0,
                message="Analysis job queued",
                started_at=datetime.now()
            )
            
            agent.active_jobs[job_id] = job_status
            
            # Verify job is tracked
            assert job_id in agent.active_jobs
            assert agent.active_jobs[job_id].status == "pending"
            
            # Simulate job completion
            from multi_agent.agents.dashboard_agent import AnalysisResult, ReportInfo
            result = AnalysisResult(
                job_id=job_id,
                status="completed",
                reports=[],
                generation_metadata={},
                summary_stats={},
                insights_count=5
            )
            
            agent.completed_jobs[job_id] = result
            del agent.active_jobs[job_id]
            
            # Verify job moved to completed
            assert job_id not in agent.active_jobs
            assert job_id in agent.completed_jobs
            assert agent.completed_jobs[job_id].status == "completed"
    
    def test_job_status_updates(self, agent):
        """Test job status update functionality."""
        from multi_agent.agents.dashboard_agent import AnalysisStatus
        
        job_id = "test-job-456"
        job_status = AnalysisStatus(
            job_id=job_id,
            status="pending",
            progress=0.0,
            message="Starting analysis",
            started_at=datetime.now()
        )
        
        agent.active_jobs[job_id] = job_status
        
        # Update job status
        agent.active_jobs[job_id].status = "running"
        agent.active_jobs[job_id].progress = 0.5
        agent.active_jobs[job_id].message = "Processing data"
        
        # Verify updates
        updated_job = agent.active_jobs[job_id]
        assert updated_job.status == "running"
        assert updated_job.progress == 0.5
        assert updated_job.message == "Processing data"


class TestMessageHandling:
    """Test message handling functionality."""
    
    @pytest.mark.asyncio
    async def test_handle_report_ready_success(self):
        """Test successful handling of REPORT_READY message."""
        agent = DashboardAgent()
        
        # Create test report ready message
        reports_data = {
            "reports": [
                {
                    "file_path": "output/reports/test_analysis.xlsx",
                    "report_type": "excel_analysis",
                    "created_at": datetime.now().isoformat(),
                    "size_bytes": 9224,
                    "worksheets": ["Executive Summary", "AI Insights"]
                }
            ],
            "generation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "reports_count": 1,
                "total_size_bytes": 9224
            },
            "summary_stats": {
                "returns_stats": {"total_amount": 1000.0}
            }
        }
        
        message = create_message(
            MessageType.REPORT_READY,
            AgentType.REPORT,
            AgentType.DASHBOARD,
            reports_data
        )
        
        # Mock send_message to capture response
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        # Start agent and handle message
        await agent._on_start()
        response = await agent.handle_report_ready(message)
        
        # Verify response
        assert response.type == MessageType.TASK_COMPLETED
        assert response.metadata.sender == AgentType.DASHBOARD
        assert response.metadata.recipient == AgentType.COORDINATOR
        
        # Verify payload structure
        payload = response.payload
        assert "task" in payload
        assert "reports_received" in payload
        assert "timestamp" in payload
        assert payload["reports_received"] == 1
        
        # Verify send_message was called
        assert len(sent_messages) == 1
        assert sent_messages[0].type == MessageType.TASK_COMPLETED
        
        await agent._on_stop()
    
    @pytest.mark.asyncio
    async def test_handle_report_ready_error(self):
        """Test error handling in REPORT_READY message."""
        agent = DashboardAgent()
        
        # Create malformed message
        invalid_message = create_message(
            MessageType.REPORT_READY,
            AgentType.REPORT,
            AgentType.DASHBOARD,
            {"invalid": "data"}  # Missing required fields
        )
        
        # Mock send_message to capture error response
        sent_messages = []
        agent.send_message = AsyncMock(side_effect=lambda msg: sent_messages.append(msg))
        
        await agent._on_start()
        
        # Handle message should raise exception
        with pytest.raises(Exception):
            await agent.handle_report_ready(invalid_message)
        
        # Verify error response was sent
        assert len(sent_messages) == 1
        error_msg = sent_messages[0]
        assert error_msg.type == MessageType.TASK_FAILED
        
        await agent._on_stop()


class TestAPIValidation:
    """Test API request validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        agent = DashboardAgent()
        return TestClient(agent.app)
    
    def test_analysis_request_validation(self, client):
        """Test analysis request validation."""
        # Test missing required fields
        response = client.post("/api/v1/analysis/start", json={})
        assert response.status_code == 422  # Validation error
        
        # Test invalid date format
        invalid_request = {
            "date_range_start": "invalid-date",
            "date_range_end": "2024-03-31"
        }
        response = client.post("/api/v1/analysis/start", json=invalid_request)
        assert response.status_code == 422
        
        # Test valid request
        valid_request = {
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-03-31",
            "tables": ["returns"],
            "filters": {"category": "electronics"}
        }
        response = client.post("/api/v1/analysis/start", json=valid_request)
        assert response.status_code == 200
    
    def test_file_upload_validation(self, client):
        """Test file upload validation."""
        # Test upload without file
        response = client.post("/api/v1/data/upload")
        assert response.status_code == 422  # Validation error
        
        # Test valid file upload
        test_content = b"test data"
        response = client.post(
            "/api/v1/data/upload",
            files={"file": ("test.txt", test_content, "text/plain")}
        )
        assert response.status_code == 200


class TestDashboardAgentStatistics:
    """Test agent statistics and monitoring."""
    
    def test_get_dashboard_stats(self):
        """Test dashboard agent statistics collection."""
        agent = DashboardAgent()
        
        stats = agent.get_dashboard_stats()
        
        assert "agent_type" in stats
        assert "agent_name" in stats
        assert "active_jobs" in stats
        assert "completed_jobs" in stats
        assert "server_host" in stats
        assert "server_port" in stats
        assert "cors_origins" in stats
        
        assert stats["agent_type"] == AgentType.DASHBOARD.value
        assert stats["active_jobs"] == 0
        assert stats["completed_jobs"] == 0
        assert stats["server_host"] == "127.0.0.1"
        assert stats["server_port"] == 8000
    
    def test_statistics_updates_with_jobs(self):
        """Test that statistics are updated with job changes."""
        agent = DashboardAgent()
        
        # Add mock active job
        from multi_agent.agents.dashboard_agent import AnalysisStatus
        job_status = AnalysisStatus(
            job_id="test-job",
            status="running",
            progress=0.5,
            message="Processing",
            started_at=datetime.now()
        )
        agent.active_jobs["test-job"] = job_status
        
        # Add mock completed job
        from multi_agent.agents.dashboard_agent import AnalysisResult
        result = AnalysisResult(
            job_id="completed-job",
            status="completed",
            reports=[],
            generation_metadata={},
            summary_stats={},
            insights_count=3
        )
        agent.completed_jobs["completed-job"] = result
        
        stats = agent.get_dashboard_stats()
        assert stats["active_jobs"] == 1
        assert stats["completed_jobs"] == 1


@pytest.mark.integration
class TestDashboardAgentIntegration:
    """Integration tests for dashboard agent."""
    
    @pytest.mark.asyncio
    async def test_full_api_workflow(self):
        """Test complete API workflow."""
        agent = DashboardAgent()
        client = TestClient(agent.app)
        
        await agent._on_start()
        
        try:
            # 1. Check health
            health_response = client.get("/health")
            assert health_response.status_code == 200
            
            # 2. List initial jobs (should be empty)
            jobs_response = client.get("/api/v1/analysis/jobs")
            assert jobs_response.status_code == 200
            assert len(jobs_response.json()["jobs"]) == 0
            
            # 3. Start analysis
            start_request = {
                "date_range_start": "2024-01-01",
                "date_range_end": "2024-03-31",
                "tables": ["returns", "warranties"],
                "filters": {"category": "electronics"}
            }
            
            start_response = client.post("/api/v1/analysis/start", json=start_request)
            assert start_response.status_code == 200
            job_id = start_response.json()["job_id"]
            
            # 4. Check job status
            status_response = client.get(f"/api/v1/analysis/{job_id}/status")
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            assert status_data["job_id"] == job_id
            assert status_data["status"] in ["pending", "running"]
            
            # 5. List jobs (should have one now)
            jobs_response = client.get("/api/v1/analysis/jobs")
            assert jobs_response.status_code == 200
            assert len(jobs_response.json()["jobs"]) == 1
            
            # 6. List reports
            reports_response = client.get("/api/v1/reports")
            assert reports_response.status_code == 200
            
            # 7. Upload a test file
            test_content = b"sample,data\n1,test\n2,data"
            upload_response = client.post(
                "/api/v1/data/upload",
                files={"file": ("sample.csv", test_content, "text/csv")}
            )
            assert upload_response.status_code == 200
            
            upload_data = upload_response.json()
            assert upload_data["filename"] == "sample.csv"
            assert upload_data["size"] == len(test_content)
            
        finally:
            await agent._on_stop()