from fastapi import Request

def mount_dynamic_routes(app, config, logger):

    routes = config.get("routes", [])

    for route in routes:
        path = route.get("path")
        method = route.get("method", "GET").upper()
        response_data = route.get("response", {})
        echo = route.get("echo", False)

        if not path:
            continue

        logger.info(f"Mounting dynamic route: {method} {path}")

        def create_handler(response_data, echo):

            async def handler(request: Request):
                if echo:
                    try:
                        body = await request.json()
                        return {"echo": body}
                    except Exception:
                        return {"error": "Invalid JSON"}
                return response_data

            return handler

        app.add_api_route(
            path,
            create_handler(response_data, echo),
            methods=[method],
        )