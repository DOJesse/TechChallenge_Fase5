"""
logger.py

Módulo de configuração de logging para todo o projeto.
Fornece função `setup_logger` para criar loggers com handlers de console e arquivo.
"""
import logging
import os


def setup_logger(name: str,
                 log_file: str = None,
                 level: int = logging.INFO) -> logging.Logger:
    """
    Configura e retorna um logger com nome `name`.

    Se `log_file` for fornecido, cria um FileHandler no caminho especificado.
    Sempre adiciona um StreamHandler para saída no console.

    Args:
        name: nome do logger
        log_file: caminho do arquivo de log (opcional)
        level: nível de log (padrão INFO)

    Returns:
        logging.Logger configurado
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler de console
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Handler de arquivo
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


# Exemplo de uso:
# logger = setup_logger(__name__, log_file='logs/app.log')
# logger.info('Logger inicializado')
