import logging
from .formatModel import get_formatted_profile
from .regularModel import get_profile

logger = logging.getLogger(__name__)


def generate_formatted_profile(
    input_text: str,  # New parameter
    model_name: str = "gpt-4o-mini"
) -> str:  # Modified to return the response
    """
    Processes input text through LLM and stores the response.
    
    Parameters:
    - input_text: Text to be processed by the LLM
    - model_name: Language model to use
    
    Returns:
    - str: The LLM's response
    """
    try:
        logger.info(f"Processing input")
        response_formatted = get_formatted_profile(input_text)
        logger.info(f"Successfully processed and stored response")
        return response_formatted
        
    except Exception as e:
        logger.error(f"Failed to process input: {str(e)}")
        raise


def generate_regular_profile(
    input_text: str,  # New parameter
    model_name: str = "gpt-4o-mini"
) -> str:  # Modified to return the response
    logger.info(f"Processing input")
    response_regular = get_profile(input_text)
    logger.info(f"Successfully processed and stored response")
    return response_regular