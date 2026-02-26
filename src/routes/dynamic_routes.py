from fastapi import Request
from src.engine.controller_engine import execute_controller
from src.utils.db import get_db


def mount_dynamic_routes(app, config, logger):

    db = get_db()
    routes = config.get("routes", [])

    for route_ref in routes:

        route_id = route_ref.get("route_id")

        if not route_id:
            continue

        # fetch full route definition from DB
        route_config = db["routes"].find_one({"_id": route_id})

        if not route_config:
            logger.error(f"Route config not found: {route_id}")
            continue

        path = route_config.get("path")
        method = route_config.get("method", "GET").upper()
        controller_id = route_config.get("controller_id")

        if not path or not controller_id:
            logger.error(f"Invalid route config: {route_id}")
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