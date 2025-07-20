"""
Serviço de predição centralizado
"""

import logging
from typing import Dict, Tuple, Any, Optional
from src.core.config import config
from src.core.exceptions import ModelLoadError, PredictionError, DataValidationError
from src.models.predict import PredictionPipeline


logger = logging.getLogger(__name__)


class PredictionService:
    """Serviço responsável por todas as operações de predição"""
    
    def __init__(self):
        self._pipeline: Optional[PredictionPipeline] = None
        self._load_pipeline()
    
    def _load_pipeline(self) -> None:
        """Carrega o pipeline de predição"""
        try:
            self._pipeline = PredictionPipeline(
                model_path=config.model.model_path,
                artifacts_path=config.model.artifacts_path,
                w2v_model_path=config.model.w2v_model_path
            )
            logger.info("Pipeline de predição carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar pipeline: {e}")
            raise ModelLoadError(f"Falha ao carregar o modelo: {e}")
    
    def predict(self, candidate_data: Dict[str, Any], vacancy_data: Dict[str, Any]) -> Tuple[float, Any]:
        """
        Realiza predição para um candidato e vaga
        
        Args:
            candidate_data: Dados do candidato
            vacancy_data: Dados da vaga
            
        Returns:
            Tuple com score de predição e dados adicionais
            
        Raises:
            PredictionError: Se houver erro na predição
            DataValidationError: Se os dados forem inválidos
        """
        if not self._pipeline:
            raise ModelLoadError("Pipeline não está carregado")
        
        try:
            # Validar dados de entrada
            self._validate_input_data(candidate_data, vacancy_data)
            
            # Realizar predição
            prediction, additional_data = self._pipeline.predict(candidate_data, vacancy_data)
            
            logger.info(f"Predição realizada com sucesso: {prediction}")
            return prediction, additional_data
            
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            raise PredictionError(f"Falha na predição: {e}")
    
    def _validate_input_data(self, candidate_data: Dict[str, Any], vacancy_data: Dict[str, Any]) -> None:
        """Valida dados de entrada"""
        if not candidate_data:
            raise DataValidationError("Dados do candidato não podem estar vazios")
        
        if not vacancy_data:
            raise DataValidationError("Dados da vaga não podem estar vazios")
        
        # Validações específicas podem ser adicionadas aqui
        
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do serviço"""
        return {
            "service": "prediction",
            "status": "healthy" if self._pipeline else "unhealthy",
            "pipeline_loaded": self._pipeline is not None
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações do modelo"""
        if not self._pipeline:
            return {"error": "Pipeline não carregado"}
        
        return {
            "model_loaded": True,
            "model_path": config.model.model_path,
            "artifacts_path": config.model.artifacts_path,
            "w2v_model_path": config.model.w2v_model_path
        }
