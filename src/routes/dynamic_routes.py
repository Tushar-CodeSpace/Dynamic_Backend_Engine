from fastapi import Request
from src.engine.controller_engine import execute_controller
from src.utils.db import get_db


def mount_dynamic_routes(app, config, logger):

    routes = config.get("routes", [])
    db = get_db()

    for route in routes:

        path = route.get("path")
        method = route.get("method", "GET").upper()
        controller_id = route.get("controller")

        if not path or not controller_id:
            continue

        logger.info(f"Mounting dynamic route: {method} {path}")

        def create_handler(controller_id):

            async def handler(request: Request):

                controller_config = db["controllers"].find_one(
                    {"_id": controller_id}
                )

                if not controller_config:
                    return {"error": "Controller not found"}

                return await execute_controller(
                    controller_config,
                    request,
                    db
                )

            return handler

        app.add_api_route(
            path,
            create_handler(controller_id),
            methods=[method]
        )