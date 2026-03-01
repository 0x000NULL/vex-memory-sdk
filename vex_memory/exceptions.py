"""
Exception classes for vex-memory SDK.
"""


class VexMemoryError(Exception):
    """Base exception for vex-memory SDK."""
    pass


class VexMemoryAPIError(VexMemoryError):
    """API request failed."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class VexMemoryValidationError(VexMemoryError):
    """Invalid parameters provided."""
    pass
