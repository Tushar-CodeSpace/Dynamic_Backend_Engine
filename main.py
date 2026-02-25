from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from src.utils.logger import logger
from src.utils.db import get_app_config, close_db
from src.routes.dynamic_routes import mount_dynamic_routes
from src.middleware.request_logger import setup_request_logger

app = FastAPI()

setup_request_logger(app, logger)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Getting config from database")

    config = get_app_config()
    app.state.config = config

    logger.set_debug(config.get("debug", False))
    logger.debug(f"Config found :: {config}")

    mount_dynamic_routes(app, config, logger)
    


    logger.info("App is online")
    yield
    print()
    logger.info("App shutting down")
    close_db()

app.router.lifespan_context = lifespan



if __name__ == "__main__":

    config = get_app_config()
    port = int(config.get("port", 3000))

    logger.info(f"Listening on port {port}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="critical",
        access_log=False
    )