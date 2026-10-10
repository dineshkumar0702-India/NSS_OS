from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class Problem(HTTPException):
    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str,
        code: str,
        instance: str | None = None,
        confirm_token: str | None = None,
    ) -> None:
        self.problem = {
            "type": f"https://opennas.local/errors/{code.lower().replace('_', '-')}",
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": instance,
            "code": code,
            "confirm_token": confirm_token,
        }
        super().__init__(status_code=status_code, detail=detail)


def problem_exception_handler(_request: Request, exc: Problem) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.problem)
