import time
from fastapi import Request
from starlette.responses import Response


def setup_request_logger(app, logger):

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()

        try:
            response: Response = await call_next(request)
        except Exception as e:
            duration = round((time.time() - start) * 1000, 2)
            logger.error(
                f"{request.client.host} {request.method} {request.url.path} 500 {duration}ms EXC={e}"
            )
            raise

        duration = round((time.time() - start) * 1000, 2)

        msg = (
            f"{request.client.host} "
            f"{request.method} {request.url.path} "
            f"{response.status_code} "
            f"{duration}ms"
        )

        if response.status_code >= 500:
            logger.error(msg)
        elif response.status_code >= 400:
            logger.warn(msg)
        else:
            logger.info(msg)

        return response