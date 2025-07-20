"""
Exceções customizadas do projeto
"""


class TechChallengeException(Exception):
    """Exceção base do projeto"""
    pass


class ModelLoadError(TechChallengeException):
    """Erro ao carregar modelo"""
    pass


class PredictionError(TechChallengeException):
    """Erro durante predição"""
    pass


class DataValidationError(TechChallengeException):
    """Erro de validação de dados"""
    pass


class FileProcessingError(TechChallengeException):
    """Erro no processamento de arquivos"""
    pass


class ConfigurationError(TechChallengeException):
    """Erro de configuração"""
    pass
