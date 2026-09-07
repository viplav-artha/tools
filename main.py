import os
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, create_model

from tools import search_tool  # noqa: F401 (side effect: registers web_search)
from tools.registry import call_tool, get_tool_specs

load_dotenv()

app = FastAPI(
    title="Tools API",
    description="One endpoint per registered tool, calling it the same way an LLM would.",
)

_JSON_TYPE_MAP: dict[str, Any] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _build_request_model(tool_name: str, schema: dict) -> type[BaseModel]:
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    fields: dict[str, Any] = {}
    for name, prop in properties.items():
        python_type = _JSON_TYPE_MAP.get(prop.get("type"), str)
        description = prop.get("description", "")

        if name in required:
            fields[name] = (python_type, Field(..., description=description))
        else:
            fields[name] = (Optional[python_type], Field(None, description=description))

    model_name = "".join(part.capitalize() for part in tool_name.split("_")) + "Request"
    return create_model(model_name, **fields)


def _make_endpoint(tool_name: str, request_model: type[BaseModel]):
    async def endpoint(payload: request_model):  # type: ignore[valid-type]
        arguments = payload.model_dump(exclude_none=True)
        result = await call_tool(tool_name, arguments)
        return {"tool": tool_name, "arguments": arguments, "result": result}

    return endpoint


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


for spec in get_tool_specs():
    tool_spec = spec["toolSpec"]
    name = tool_spec["name"]
    request_model = _build_request_model(name, tool_spec["inputSchema"]["json"])

    app.add_api_route(
        f"/tools/{name}",
        _make_endpoint(name, request_model),
        methods=["POST"],
        summary=name,
        description=tool_spec["description"],
        tags=["tools"],
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8100"))
    uvicorn.run(app, host="0.0.0.0", port=port)
