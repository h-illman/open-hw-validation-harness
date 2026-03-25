"""
Basic logging utilities for the validation harness.
"""
import logging

def get_logger(name):
    """
    Returns a configured minimal logger instance.
    
    Args:
        name: The name of the logger to retrieve
        
    Returns:
        logging.Logger: configured logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
