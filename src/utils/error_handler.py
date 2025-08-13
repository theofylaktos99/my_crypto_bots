# error_handler.py - Error Handling Utilities
import logging
import traceback
from typing import Optional, Any, Callable
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling utility"""
    
    @staticmethod
    def handle_exception(error: Exception, context: str = "", reraise: bool = True) -> Optional[Any]:
        """
        Handle exceptions with logging and optional re-raising
        
        Args:
            error: The exception to handle
            context: Additional context information
            reraise: Whether to re-raise the exception after logging
        """
        error_msg = f"Error in {context}: {str(error)}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        if reraise:
            raise error
        return None
    
    @staticmethod
    def safe_execute(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
        """
        Safely execute a function and return success status with result
        
        Returns:
            (success: bool, result: Any)
        """
        try:
            result = func(*args, **kwargs)
            return True, result
        except Exception as e:
            ErrorHandler.handle_exception(e, f"executing {func.__name__}", reraise=False)
            return False, None
    
    @staticmethod
    async def safe_execute_async(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
        """
        Safely execute an async function
        
        Returns:
            (success: bool, result: Any)
        """
        try:
            result = await func(*args, **kwargs)
            return True, result
        except Exception as e:
            ErrorHandler.handle_exception(e, f"executing async {func.__name__}", reraise=False)
            return False, None

def handle_errors(context: str = "", reraise: bool = False):
    """
    Decorator for error handling
    
    Args:
        context: Context description for logging
        reraise: Whether to re-raise exceptions
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_exception(e, context or func.__name__, reraise)
                return None
        return wrapper
    return decorator

def handle_errors_async(context: str = "", reraise: bool = False):
    """
    Async decorator for error handling
    
    Args:
        context: Context description for logging
        reraise: Whether to re-raise exceptions
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_exception(e, context or func.__name__, reraise)
                return None
        return wrapper
    return decorator

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

class TradingError(Exception):
    """Custom exception for trading-related errors"""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass
