import traceback

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class ErrorHandler:
    """
    Centralized error handler for FastAPI that provides informative and consistent error responses.
    """

    def __init__(self, app: FastAPI, logger) -> None:
        """
        Initializes the ErrorHandler and registers error handlers.

        Args:
            app: FastAPI application instance.
            logger: Logger instance used to record error details.
        """
        self._register_error_handlers(app)
        self._logger = logger

    @staticmethod
    def _error_response(
            request: Request,
            error_type: str,
            message: str,
            http_status: int,
            details: dict | list | None = None,
    ) -> JSONResponse:
        """
        Builds a standardized JSON error response.

        Args:
            request: FastAPI request object.
            error_type: Type of the error (e.g. "ValidationError").
            message: Main error message.
            http_status: HTTP status code.
            details: Optional detailed error information.

        Returns:
            JSONResponse: Formatted JSON response containing error details.
        """
        response_content = {
            'error': {
                'type': error_type,
                'message': message,
                'path': request.url.path,
                'method': request.method,
                'details': details,
            }
        }
        response = JSONResponse(status_code=http_status, content=response_content)

        return response

    def _register_error_handlers(self, app: FastAPI) -> None:
        """
        Registers all custom error handlers for FastAPI.

        Args:
            app: FastAPI application instance.

        Returns:
            None: This method modifies the app in place.
        """

        @app.exception_handler(HTTPException)
        async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
            """
            Handles FastAPI HTTPException errors.

            Args:
                request: FastAPI request object.
                exc: Raised HTTPException.

            Returns:
                JSONResponse: JSON response describing the HTTP error.
            """
            self._logger.warning(f"HTTP error at {request.url.path}: {exc.detail}")

            response = self._error_response(
                request=request,
                error_type='HTTPException',
                message=str(exc.detail),
                http_status=exc.status_code,
            )

            return response

        @app.exception_handler(ValidationError)
        async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
            """
            Handles Pydantic validation errors.

            Args:
                request: FastAPI request object.
                exc: Raised ValidationError.

            Returns:
                JSONResponse: JSON response describing the validation error.
            """
            self._logger.debug(f"Validation error: {exc.errors()}")

            response = self._error_response(
                request=request,
                error_type='ValidationError',
                message='Invalid input data',
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=exc.errors(),
            )

            return response

        @app.exception_handler(ValueError)
        async def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
            """
            Handles Python ValueError exceptions.

            Args:
                request: FastAPI request object.
                exc: Raised ValueError.

            Returns:
                JSONResponse: JSON response describing the value error.
            """
            self._logger.warning(f"Value error: {exc}")

            response = self._error_response(
                request=request,
                error_type='ValueError',
                message=str(exc),
                http_status=status.HTTP_400_BAD_REQUEST,
            )

            return response

        @app.exception_handler(Exception)
        async def handle_general_exception(request: Request, exc: Exception) -> JSONResponse:
            """
            Handles all unexpected exceptions.

            Args:
                request: FastAPI request object.
                exc: Raised Exception.

            Returns:
                JSONResponse: JSON response describing the internal server error.
            """
            # Generate traceback and log error
            traceback_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            self._logger.error(f"Unhandled exception at {request.url.path}: {exc}\n{traceback_str}")

            response = self._error_response(
                request=request,
                error_type=exc.__class__.__name__,
                message='Internal server error occurred',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={'traceback': traceback_str.splitlines()[-5:]},
            )

            return response
