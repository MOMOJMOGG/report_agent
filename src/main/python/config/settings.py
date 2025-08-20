"""
Application configuration settings.
Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str = "sqlite:///retail_data.db"
    echo: bool = False
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            url=os.getenv('DATABASE_URL', cls.url),
            echo=os.getenv('DATABASE_ECHO', str(cls.echo)).lower() == 'true'
        )


@dataclass
class OpenAIConfig:
    """OpenAI API configuration settings."""
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 150
    temperature: float = 0.3
    
    @classmethod
    def from_env(cls) -> 'OpenAIConfig':
        return cls(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=os.getenv('OPENAI_MODEL', cls.model),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', str(cls.max_tokens))),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', str(cls.temperature)))
        )


@dataclass
class RAGConfig:
    """RAG Agent configuration settings."""
    enable_mock_mode: bool = False
    max_api_calls_per_session: int = 10
    similarity_threshold: float = 0.2
    top_k_retrieval: int = 5
    cache_ttl_hours: int = 24
    enable_caching: bool = True
    
    @classmethod
    def from_env(cls) -> 'RAGConfig':
        return cls(
            enable_mock_mode=os.getenv('RAG_ENABLE_MOCK_MODE', str(cls.enable_mock_mode)).lower() == 'true',
            max_api_calls_per_session=int(os.getenv('RAG_MAX_API_CALLS_PER_SESSION', str(cls.max_api_calls_per_session))),
            similarity_threshold=float(os.getenv('RAG_SIMILARITY_THRESHOLD', str(cls.similarity_threshold))),
            top_k_retrieval=int(os.getenv('RAG_TOP_K_RETRIEVAL', str(cls.top_k_retrieval))),
            cache_ttl_hours=int(os.getenv('RAG_CACHE_TTL_HOURS', str(cls.cache_ttl_hours))),
            enable_caching=os.getenv('RAG_ENABLE_CACHING', str(cls.enable_caching)).lower() == 'true'
        )


@dataclass
class ReportConfig:
    """Report Agent configuration settings."""
    output_directory: str = "output/reports"
    file_prefix: str = "retail_analysis"
    include_timestamp: bool = True
    create_charts: bool = True
    auto_adjust_columns: bool = True
    
    @classmethod
    def from_env(cls) -> 'ReportConfig':
        return cls(
            output_directory=os.getenv('REPORT_OUTPUT_DIRECTORY', cls.output_directory),
            file_prefix=os.getenv('REPORT_FILE_PREFIX', cls.file_prefix),
            include_timestamp=os.getenv('REPORT_INCLUDE_TIMESTAMP', str(cls.include_timestamp)).lower() == 'true',
            create_charts=os.getenv('REPORT_CREATE_CHARTS', str(cls.create_charts)).lower() == 'true',
            auto_adjust_columns=os.getenv('REPORT_AUTO_ADJUST_COLUMNS', str(cls.auto_adjust_columns)).lower() == 'true'
        )


@dataclass
class DashboardConfig:
    """Dashboard Agent configuration settings."""
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = None
    max_file_size_mb: int = 10
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @classmethod
    def from_env(cls) -> 'DashboardConfig':
        cors_origins_str = os.getenv('DASHBOARD_CORS_ORIGINS', '')
        cors_origins = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()] if cors_origins_str else None
        
        return cls(
            host=os.getenv('DASHBOARD_HOST', cls.host),
            port=int(os.getenv('DASHBOARD_PORT', str(cls.port))),
            debug=os.getenv('DASHBOARD_DEBUG', str(cls.debug)).lower() == 'true',
            cors_origins=cors_origins,
            max_file_size_mb=int(os.getenv('DASHBOARD_MAX_FILE_SIZE_MB', str(cls.max_file_size_mb)))
        )


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_secret_key: str = "dev-jwt-secret-change-in-production"
    jwt_expiration_hours: int = 24
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        return cls(
            secret_key=os.getenv('SECRET_KEY', cls.secret_key),
            jwt_secret_key=os.getenv('JWT_SECRET_KEY', cls.jwt_secret_key),
            jwt_expiration_hours=int(os.getenv('JWT_EXPIRATION_HOURS', str(cls.jwt_expiration_hours)))
        )


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        return cls(
            level=os.getenv('LOG_LEVEL', cls.level),
            format=os.getenv('LOG_FORMAT', cls.format)
        )


@dataclass
class AppSettings:
    """Main application settings container."""
    database: DatabaseConfig
    openai: OpenAIConfig
    rag: RAGConfig
    report: ReportConfig
    dashboard: DashboardConfig
    security: SecurityConfig
    logging: LoggingConfig
    
    @classmethod
    def from_env(cls) -> 'AppSettings':
        """Load all configuration from environment variables."""
        return cls(
            database=DatabaseConfig.from_env(),
            openai=OpenAIConfig.from_env(),
            rag=RAGConfig.from_env(),
            report=ReportConfig.from_env(),
            dashboard=DashboardConfig.from_env(),
            security=SecurityConfig.from_env(),
            logging=LoggingConfig.from_env()
        )


# Global settings instance
settings = AppSettings.from_env()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def ensure_directories():
    """Ensure required directories exist."""
    dirs_to_create = [
        settings.report.output_directory,
        "logs",
        "data/raw",
        "data/processed",
        "output/dashboards"
    ]
    
    project_root = get_project_root()
    for dir_path in dirs_to_create:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)


# Initialize directories on import
ensure_directories()