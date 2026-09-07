from typing import Awaitable, Callable

_TOOL_SPECS: list[dict] = []
_TOOL_FUNCTIONS: dict[str, Callable[..., Awaitable]] = {}


def tool(name: str, description: str, input_schema: dict) -> Callable:
    def decorator(func: Callable) -> Callable:
        _TOOL_SPECS.append(
            {
                "toolSpec": {
                    "name": name,
                    "description": description,
                    "inputSchema": {"json": input_schema},
                }
            }
        )
        _TOOL_FUNCTIONS[name] = func
        return func

    return decorator


def get_tool_specs() -> list[dict]:
    return _TOOL_SPECS


async def call_tool(name: str, arguments: dict):
    if name not in _TOOL_FUNCTIONS:
        raise ValueError(f"Unknown tool: {name}")
    return await _TOOL_FUNCTIONS[name](**arguments)
