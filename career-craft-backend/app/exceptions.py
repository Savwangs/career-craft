class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    def __init__(self, message: str = "A database error occurred"):
        self.message = message
        super().__init__(self.message)