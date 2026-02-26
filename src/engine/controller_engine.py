from passlib.hash import bcrypt
from datetime import datetime
import uuid


async def execute_controller(controller_config, request, db):

    controller_type = controller_config.get("type")

    if controller_type == "auth_signup":

        body = await request.json()

        collection_name = controller_config["collection"]
        fields_config = controller_config.get("fields", {})

        users = db[collection_name]

        # 🔎 Validate required fields
        for field_name, rules in fields_config.items():
            if rules.get("required") and field_name not in body:
                return {
                    "error": f"Field '{field_name}' is required"
                }

        # 🔎 Unique check
        for field_name, rules in fields_config.items():
            if rules.get("unique"):
                if users.find_one({field_name: body.get(field_name)}):
                    return {
                        "error": f"{field_name} already exists"
                    }

        # 🔐 Hash password if configured
        for field_name, rules in fields_config.items():
            if rules.get("hash") and field_name in body:
                body[field_name] = bcrypt.hash(body[field_name])

        # ➕ Add defaults
        defaults = controller_config.get("defaults", {})
        for key, value in defaults.items():
            body.setdefault(key, value)

        # 🆔 UUID v7 as _id
        body["_id"] = str(uuid.uuid7())

        body["created_at"] = datetime.utcnow()

        users.insert_one(body)

        return {
            "status": "success",
            "user_id": body["_id"]
        }

    return {"error": "Unknown controller"}