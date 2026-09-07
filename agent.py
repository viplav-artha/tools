import asyncio

from tools import search_tool  # noqa: F401 (side effect: registers web_search)
from tools.registry import call_tool, get_tool_specs

from llm import get_llm


async def run(question: str) -> str:
    llm = get_llm()
    messages = [{"role": "user", "content": [{"text": question}]}]

    response = llm.invoke(messages, tools=get_tool_specs())
    message = response["output"]["message"]
    messages.append(message)

    if response["stopReason"] == "tool_use":
        tool_uses = [block["toolUse"] for block in message["content"] if "toolUse" in block]
        results = await asyncio.gather(
            *(call_tool(tu["name"], tu["input"]) for tu in tool_uses)
        )

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "toolResult": {
                            "toolUseId": tool_use["toolUseId"],
                            "content": [{"text": str(result)}],
                        }
                    }
                    for tool_use, result in zip(tool_uses, results)
                ],
            }
        )

        response = llm.invoke(messages, tools=get_tool_specs())
        message = response["output"]["message"]

    return "".join(block["text"] for block in message["content"] if "text" in block)


async def main():
    question = input("Ask something: ")
    print(await run(question))


if __name__ == "__main__":
    asyncio.run(main())
