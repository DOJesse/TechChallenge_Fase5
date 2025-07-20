"""
Configurações centralizadas do projeto
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Configurações do modelo"""
    model_path: str
    artifacts_path: str
    w2v_model_path: str
    min_coverage_threshold: float = 0.35
    prediction_timeout: int = 30


@dataclass
class APIConfig:
    """Configurações da API"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    cors_enabled: bool = True
    rate_limit: str = "100/hour"


@dataclass
class StreamlitConfig:
    """Configurações do Streamlit"""
    api_url: str
    max_file_size: int = 10  # MB
    supported_formats: list = None
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['pdf', 'docx']


@dataclass
class TestConfig:
    """Configurações de teste"""
    coverage_threshold: float = 0.35
    test_data_path: str = "tests/fixtures"
    mock_external_apis: bool = True


class Config:
    """Classe principal de configuração"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.src_dir = self.base_dir / "src"
        
        # Configurações do modelo
        self.model = ModelConfig(
            model_path=str(self.base_dir / "artifacts" / "model.joblib"),
            artifacts_path=str(self.base_dir / "artifacts" / "preprocessing_artifacts.joblib"),
            w2v_model_path=str(self.base_dir / "src" / "word2vec" / "cbow_s100.txt")
        )
        
        # Configurações da API
        self.api = APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "5000")),
            debug=os.getenv("DEBUG", "False").lower() == "true"
        )
        
        # Configurações do Streamlit
        self.streamlit = StreamlitConfig(
            api_url=os.getenv("API_URL", "http://localhost:5000")
        )
        
        # Configurações de teste
        self.test = TestConfig()
    
    @property
    def environment(self) -> str:
        """Retorna o ambiente atual"""
        return os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.environment == "development"
    
    @property
    def is_testing(self) -> bool:
        """Verifica se está em teste"""
        return self.environment == "testing"


# Instância global de configuração
config = Config()
