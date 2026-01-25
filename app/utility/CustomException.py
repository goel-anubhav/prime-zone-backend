from fastapi.exceptions import HTTPException

class CustomHttpException(HTTPException):
    def __init__(self, status_code: int, detail: str,message:str, headers: dict = None):
        """
        Initializes a CustomHttpException instance.

        Args:
            status_code (int): The HTTP status code of the exception.
            detail (str): A detailed description of the exception.
            message (str): A brief message describing the exception.
            headers (dict, optional): A dictionary of headers to be included in the exception response. Defaults to None.

        Returns:
            None
        """
        self.status_code = status_code
        self.detail = detail
        self.message=message
        self.headers = headers