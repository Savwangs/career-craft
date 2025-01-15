from fastapi import HTTPException
from typing import Optional

class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    def __init__(self, message: str = "A database error occurred"):
        self.message = message
        super().__init__(self.message)

class CareerCraftException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(CareerCraftException):
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        detail = f"{resource} not found"
        if resource_id:
            detail += f" with id {resource_id}"
        super().__init__(status_code=404, detail=detail)

class ValidationException(CareerCraftException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)

class AuthenticationException(CareerCraftException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)

class RateLimitException(CareerCraftException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)

class FileProcessingException(CareerCraftException):
    def __init__(self, detail: str = "File processing failed"):
        super().__init__(status_code=500, detail=detail)