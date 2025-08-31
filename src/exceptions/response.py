from typing import Optional, Union, Dict, Any

class ApiResponseResult:
    def __init__(
        self,
        success: bool,
        data: Optional[Union[Dict, Any]] = None,
        error: Optional[Union[str, Dict[str, Any]]] = None,
        message: Optional[str] = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message,
        }