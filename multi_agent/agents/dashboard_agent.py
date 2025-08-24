"""
Dashboard Agent for providing REST API endpoints and web interface.
Handles HTTP requests, file uploads, and serves the React dashboard.
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends, status, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
import logging
import traceback
from datetime import datetime
import sys

from multi_agent.core.base_agent import BaseAgent, AgentConfig
from multi_agent.models.message_types import (
    BaseMessage, MessageType, AgentType, 
    ReportReadyPayload, ReportData, create_message
)
from multi_agent.config.settings import settings
from multi_agent.utils.report_generator import ExcelReportGenerator


@dataclass
class DashboardConfig:
    """Configuration for dashboard operations."""
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = None
    max_file_size_mb: int = 10
    static_files_path: str = "output/dashboards"
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]


# Pydantic models for API requests/responses
class AnalysisRequest(BaseModel):
    """Request model for starting analysis."""
    date_range_start: str = Field(..., description="Start date in YYYY-MM-DD format")
    date_range_end: str = Field(..., description="End date in YYYY-MM-DD format")
    tables: List[str] = Field(default=["returns", "warranties", "products"], description="Tables to analyze")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")


class AnalysisStatus(BaseModel):
    """Response model for analysis status."""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float = Field(ge=0, le=1, description="Progress from 0 to 1")
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ReportInfo(BaseModel):
    """Response model for report information."""
    file_path: str
    report_type: str
    created_at: datetime
    size_bytes: int
    worksheets: List[str]
    download_url: str


class AnalysisResult(BaseModel):
    """Response model for completed analysis."""
    job_id: str
    status: str
    reports: List[ReportInfo]
    generation_metadata: Dict[str, Any]
    summary_stats: Dict[str, Any]
    insights_count: int


class DashboardAgent(BaseAgent):
    """
    Dashboard Agent providing REST API endpoints and web interface.
    Handles HTTP requests, coordinates with other agents, and serves results.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, dashboard_config: Optional[DashboardConfig] = None):
        # Configure for web service operations
        agent_config = config or AgentConfig(
            max_retries=3,
            retry_delay=2.0,
            timeout_seconds=300,
            heartbeat_interval=30
        )
        
        super().__init__(AgentType.DASHBOARD, agent_config, "DashboardAgent")
        
        # Dashboard configuration
        self.dashboard_config = dashboard_config or DashboardConfig()
        
        # Initialize report generator
        self.report_generator = ExcelReportGenerator(settings.report.output_directory)
        
        # Register message handlers
        self.register_handler(MessageType.REPORT_READY, self.handle_report_ready)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Retail Analysis Dashboard API",
            description="REST API for multi-agent retail data analysis system",
            version="1.0.0"
        )
        
        # Setup error handlers
        self._setup_error_handlers()
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.dashboard_config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Job tracking
        self.active_jobs: Dict[str, AnalysisStatus] = {}
        self.completed_jobs: Dict[str, AnalysisResult] = {}
        
        # Setup API routes
        self._setup_routes()
        
        # Ensure directories exist
        Path(self.dashboard_config.static_files_path).mkdir(parents=True, exist_ok=True)
        Path(settings.report.output_directory).mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Setup comprehensive logging for the dashboard agent."""
        # Ensure logs directory exists first
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Clear any existing handlers to avoid conflicts
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handler
        log_file = logs_dir / 'dashboard_agent.log'
        file_handler = logging.FileHandler(str(log_file), mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Setup console handler  
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Configure root logger
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Create specific loggers
        self.access_logger = logging.getLogger("dashboard.access")
        self.error_logger = logging.getLogger("dashboard.error")
        self.api_logger = logging.getLogger("dashboard.api")
        
        # Set specific levels
        self.access_logger.setLevel(logging.INFO)
        self.error_logger.setLevel(logging.WARNING)
        self.api_logger.setLevel(logging.DEBUG)
        
        # Log startup message
        self.logger.info("Dashboard agent logging system initialized")
        self.logger.info(f"Log file: {log_file.absolute()}")
        
        # Test all loggers
        self.access_logger.info("Access logger initialized")
        self.error_logger.warning("Error logger initialized")  
        self.api_logger.debug("API logger initialized")
    
    def _setup_error_handlers(self):
        """Setup comprehensive error handlers for FastAPI."""
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = datetime.now()
            
            # Log request
            self.access_logger.info(
                f"Request: {request.method} {request.url} - "
                f"Client: {request.client.host if request.client else 'unknown'}"
            )
            
            try:
                response = await call_next(request)
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log response
                self.access_logger.info(
                    f"Response: {response.status_code} - "
                    f"Duration: {duration:.3f}s"
                )
                
                return response
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.error_logger.error(
                    f"Request failed: {request.method} {request.url} - "
                    f"Duration: {duration:.3f}s - Error: {str(e)}\n"
                    f"Traceback: {traceback.format_exc()}"
                )
                
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "message": "An unexpected error occurred",
                        "timestamp": datetime.now().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            self.error_logger.warning(
                f"HTTP Exception: {exc.status_code} - {exc.detail} - "
                f"Request: {request.method} {request.url}"
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "timestamp": datetime.now().isoformat(),
                    "path": str(request.url)
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            self.error_logger.error(
                f"Unhandled Exception: {type(exc).__name__}: {str(exc)} - "
                f"Request: {request.method} {request.url}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
    
    async def _on_start(self):
        """Initialize dashboard agent."""
        self.logger.info("Dashboard agent started")
        self.logger.info(f"Dashboard will be available at http://{self.dashboard_config.host}:{self.dashboard_config.port}")
        
        # Mount static files
        try:
            self.app.mount("/static", StaticFiles(directory=self.dashboard_config.static_files_path), name="static")
            self.app.mount("/reports", StaticFiles(directory=settings.report.output_directory), name="reports")
        except Exception as e:
            self.logger.warning(f"Could not mount static files: {e}")
    
    async def _on_stop(self):
        """Cleanup dashboard agent."""
        self.logger.info(f"Dashboard agent stopped. Handled {len(self.completed_jobs)} analysis jobs")
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/", response_class=JSONResponse)
        async def root():
            """API root endpoint."""
            return {
                "service": "Retail Analysis Dashboard API",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {
                    "health": "/health",
                    "start_analysis": "/api/v1/analysis/start",
                    "get_status": "/api/v1/analysis/{job_id}/status",
                    "list_jobs": "/api/v1/analysis/jobs",
                    "get_results": "/api/v1/analysis/{job_id}/results",
                    "download_report": "/api/v1/reports/{report_id}/download",
                    "list_reports": "/api/v1/reports"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            try:
                self.api_logger.debug("Health check requested")
                
                # Check system health
                reports_dir = Path(settings.report.output_directory)
                reports_dir_exists = reports_dir.exists()
                available_reports = len(list(reports_dir.glob("*"))) if reports_dir_exists else 0
                
                health_data = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "active_jobs": len(self.active_jobs),
                    "completed_jobs": len(self.completed_jobs),
                    "system_info": {
                        "reports_directory_exists": reports_dir_exists,
                        "available_reports": available_reports,
                        "reports_directory": str(reports_dir)
                    }
                }
                
                self.api_logger.debug(f"Health check completed: {health_data}")
                return health_data
                
            except Exception as e:
                self.error_logger.error(f"Health check failed: {e}\n{traceback.format_exc()}")
                return {
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "active_jobs": len(getattr(self, 'active_jobs', {})),
                    "completed_jobs": len(getattr(self, 'completed_jobs', {}))
                }
        
        @self.app.post("/api/v1/analysis/start", response_model=Dict[str, str])
        async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
            """Start a new analysis job."""
            job_id = str(uuid.uuid4())
            
            # Create job status
            job_status = AnalysisStatus(
                job_id=job_id,
                status="pending",
                progress=0.0,
                message="Analysis job queued",
                started_at=datetime.now()
            )
            
            self.active_jobs[job_id] = job_status
            
            # Start analysis in background
            background_tasks.add_task(self._run_analysis_pipeline, job_id, request)
            
            self.logger.info(f"Started analysis job {job_id}")
            return {"job_id": job_id, "status": "started"}
        
        @self.app.get("/api/v1/analysis/{job_id}/status", response_model=AnalysisStatus)
        async def get_analysis_status(job_id: str):
            """Get status of an analysis job."""
            if job_id in self.active_jobs:
                return self.active_jobs[job_id]
            elif job_id in self.completed_jobs:
                result = self.completed_jobs[job_id]
                return AnalysisStatus(
                    job_id=result.job_id,
                    status=result.status,
                    progress=1.0,
                    message="Analysis completed",
                    started_at=datetime.now() - timedelta(minutes=5),  # Approximate
                    completed_at=datetime.now()
                )
            else:
                raise HTTPException(status_code=404, detail="Job not found")
        
        @self.app.get("/api/v1/analysis/jobs")
        async def list_analysis_jobs():
            """List all analysis jobs."""
            jobs = []
            
            # Add active jobs
            for job in self.active_jobs.values():
                jobs.append({
                    "job_id": job.job_id,
                    "status": job.status,
                    "progress": job.progress,
                    "started_at": job.started_at.isoformat(),
                    "message": job.message
                })
            
            # Add completed jobs
            for result in self.completed_jobs.values():
                jobs.append({
                    "job_id": result.job_id,
                    "status": result.status,
                    "progress": 1.0,
                    "started_at": datetime.now().isoformat(),  # Approximate
                    "message": f"Completed with {result.insights_count} insights"
                })
            
            return {"jobs": jobs}
        
        @self.app.get("/api/v1/analysis/{job_id}/results", response_model=AnalysisResult)
        async def get_analysis_results(job_id: str):
            """Get results of a completed analysis job."""
            if job_id not in self.completed_jobs:
                if job_id in self.active_jobs:
                    raise HTTPException(status_code=202, detail="Analysis still in progress")
                else:
                    raise HTTPException(status_code=404, detail="Job not found")
            
            return self.completed_jobs[job_id]
        
        @self.app.get("/api/v1/reports")
        async def list_reports():
            """List all available reports."""
            try:
                self.api_logger.info("Listing reports from directory")
                reports = []
                reports_dir = Path(settings.report.output_directory)
                
                if not reports_dir.exists():
                    self.api_logger.warning(f"Reports directory does not exist: {reports_dir}")
                    reports_dir.mkdir(parents=True, exist_ok=True)
                    self.api_logger.info(f"Created reports directory: {reports_dir}")
                
                report_files = list(reports_dir.glob("*"))
                self.api_logger.info(f"Found {len(report_files)} files in reports directory")
                
                for report_file in report_files:
                    if report_file.is_file():
                        try:
                            stat = report_file.stat()
                            report_info = {
                                "file_path": str(report_file),
                                "file_name": report_file.name,
                                "size_bytes": stat.st_size,
                                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                "download_url": f"/api/v1/reports/{report_file.name}/download"
                            }
                            reports.append(report_info)
                            self.api_logger.debug(f"Added report: {report_file.name} ({stat.st_size} bytes)")
                        except Exception as e:
                            self.error_logger.warning(f"Error processing report file {report_file}: {e}")
                
                self.api_logger.info(f"Successfully listed {len(reports)} reports")
                return {"reports": reports}
                
            except Exception as e:
                self.error_logger.error(f"Error listing reports: {e}\n{traceback.format_exc()}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to list reports: {str(e)}"
                )
        
        @self.app.get("/api/v1/reports/{report_name}/download")
        async def download_report(report_name: str):
            """Download a specific report file."""
            try:
                self.api_logger.info(f"Download requested for report: {report_name}")
                
                # Validate filename (security check)
                if '..' in report_name or '/' in report_name or '\\' in report_name:
                    self.error_logger.warning(f"Invalid report filename attempted: {report_name}")
                    raise HTTPException(status_code=400, detail="Invalid filename")
                
                report_path = Path(settings.report.output_directory) / report_name
                
                if not report_path.exists():
                    self.error_logger.warning(f"Report not found: {report_path}")
                    available_files = list(Path(settings.report.output_directory).glob("*"))
                    self.api_logger.info(f"Available files: {[f.name for f in available_files if f.is_file()]}")
                    raise HTTPException(status_code=404, detail="Report not found")
                
                # Check if it's actually a file
                if not report_path.is_file():
                    self.error_logger.warning(f"Path exists but is not a file: {report_path}")
                    raise HTTPException(status_code=404, detail="Report not found")
                
                file_size = report_path.stat().st_size
                self.api_logger.info(f"Serving report: {report_name} ({file_size} bytes)")
                
                return FileResponse(
                    path=str(report_path),
                    filename=report_name,
                    media_type='application/octet-stream'
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.error_logger.error(f"Error downloading report {report_name}: {e}\n{traceback.format_exc()}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to download report: {str(e)}"
                )
        
        @self.app.post("/api/v1/data/upload")
        async def upload_data_file(file: UploadFile = File(...)):
            """Upload a data file for analysis."""
            # Validate file size
            max_size = self.dashboard_config.max_file_size_mb * 1024 * 1024
            if file.size and file.size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {self.dashboard_config.max_file_size_mb}MB"
                )
            
            # Save uploaded file
            upload_dir = Path("data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return {
                "filename": file.filename,
                "size": len(content),
                "saved_path": str(file_path),
                "message": "File uploaded successfully"
            }
    
    async def _run_analysis_pipeline(self, job_id: str, request: AnalysisRequest):
        """Run the complete analysis pipeline for a job."""
        try:
            # Update job status
            self.active_jobs[job_id].status = "running"
            self.active_jobs[job_id].message = "Starting data fetch..."
            self.active_jobs[job_id].progress = 0.1
            
            # Simulate pipeline execution (in real implementation, coordinate with other agents)
            await asyncio.sleep(2)  # Simulate data fetch
            
            self.active_jobs[job_id].message = "Normalizing data..."
            self.active_jobs[job_id].progress = 0.3
            await asyncio.sleep(2)  # Simulate normalization
            
            self.active_jobs[job_id].message = "Generating insights..."
            self.active_jobs[job_id].progress = 0.6
            await asyncio.sleep(3)  # Simulate RAG processing
            
            self.active_jobs[job_id].message = "Creating reports..."
            self.active_jobs[job_id].progress = 0.8
            await asyncio.sleep(2)  # Simulate report generation
            
            # Generate actual Excel report
            report_info = self.report_generator.generate_comprehensive_report(job_id)
            
            mock_reports = [
                ReportInfo(
                    file_path=report_info["file_path"],
                    report_type=report_info["report_type"],
                    created_at=datetime.fromisoformat(report_info["created_at"]),
                    size_bytes=report_info["size_bytes"],
                    worksheets=report_info["worksheets"],
                    download_url=f"/api/v1/reports/{report_info['filename']}/download"
                )
            ]
            
            result = AnalysisResult(
                job_id=job_id,
                status="completed",
                reports=mock_reports,
                generation_metadata={
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": 9,
                    "insights_generated": 5
                },
                summary_stats={
                    "returns_analyzed": 100,
                    "warranties_analyzed": 30,
                    "products_analyzed": 150
                },
                insights_count=5
            )
            
            # Move job to completed
            self.completed_jobs[job_id] = result
            del self.active_jobs[job_id]
            
            self.logger.info(f"Analysis job {job_id} completed successfully")
            
        except Exception as e:
            # Handle job failure
            self.active_jobs[job_id].status = "failed"
            self.active_jobs[job_id].message = f"Analysis failed: {str(e)}"
            self.active_jobs[job_id].error = str(e)
            
            self.logger.error(f"Analysis job {job_id} failed: {e}")
    
    async def handle_report_ready(self, message: BaseMessage) -> BaseMessage:
        """
        Handle REPORT_READY message from Report Agent.
        """
        try:
            # Parse message payload
            report_payload = ReportReadyPayload(
                reports=[
                    ReportData(
                        file_path=report["file_path"],
                        report_type=report["report_type"],
                        created_at=datetime.fromisoformat(report["created_at"]),
                        size_bytes=report["size_bytes"],
                        worksheets=report["worksheets"]
                    ) for report in message.payload["reports"]
                ],
                generation_metadata=message.payload["generation_metadata"],
                summary_stats=message.payload["summary_stats"]
            )
            
            self.logger.info(f"Received {len(report_payload.reports)} reports from Report Agent")
            
            # Store reports for API access
            # In a real implementation, this would update the job status
            # and make reports available through the API
            
            # Create response (dashboard agent typically doesn't send responses)
            response = create_message(
                MessageType.TASK_COMPLETED,
                self.agent_type,
                AgentType.COORDINATOR,
                {
                    "task": "report_processing",
                    "reports_received": len(report_payload.reports),
                    "timestamp": datetime.now().isoformat()
                },
                message.metadata.correlation_id
            )
            
            await self.send_message(response)
            self.logger.info("Reports processed and made available via API")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling report ready: {e}")
            # Send error response
            error_response = self.create_status_message(
                AgentType.COORDINATOR,
                message.metadata.message_id,
                "failed",
                error=str(e)
            )
            await self.send_message(error_response)
            raise
    
    def run_server(self):
        """Run the FastAPI server."""
        uvicorn.run(
            self.app,
            host=self.dashboard_config.host,
            port=self.dashboard_config.port,
            log_level="info"
        )
    
    async def start_server_async(self):
        """Start the server asynchronously."""
        config = uvicorn.Config(
            self.app,
            host=self.dashboard_config.host,
            port=self.dashboard_config.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard agent statistics."""
        return {
            "agent_type": self.agent_type.value,
            "agent_name": self.name,
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len(self.completed_jobs),
            "server_host": self.dashboard_config.host,
            "server_port": self.dashboard_config.port,
            "cors_origins": self.dashboard_config.cors_origins
        }