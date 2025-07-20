"""
Constantes do projeto
"""

# Versão da API
API_VERSION = "1.0.0"

# Timeouts
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300

# Limites de arquivo
MAX_FILE_SIZE_MB = 10
MAX_FILES_PER_REQUEST = 10

# Formatos suportados
SUPPORTED_PDF_EXTENSIONS = ['.pdf']
SUPPORTED_DOCUMENT_EXTENSIONS = ['.docx', '.doc']
SUPPORTED_TEXT_EXTENSIONS = ['.txt']

# Métricas
MIN_COVERAGE_THRESHOLD = 0.35
TARGET_COVERAGE_THRESHOLD = 0.80

# Códigos de status customizados
STATUS_MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
STATUS_INVALID_INPUT = "INVALID_INPUT"
STATUS_PROCESSING_ERROR = "PROCESSING_ERROR"
STATUS_SUCCESS = "SUCCESS"

# Headers HTTP
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_XML = "application/xml"

# Logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
