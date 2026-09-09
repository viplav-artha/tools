import asyncio
import json

from tools import get_current_time, web_search  # noqa: F401 (registers tools)
from tools.registry import call_tool, get_tool_specs

from llm import get_llm


def _dump(label: str, obj) -> None:
    print(f"\n--- {label} ---")
    print(json.dumps(obj, indent=2, default=str))


async def run(question: str) -> str:
    llm = get_llm()
    messages = [{"role": "user", "content": [{"text": question}]}]

    print(f"\n[1] Sending question to the model: {question!r}")
    _dump("Outgoing messages", messages)

    response = llm.invoke(messages, tools=get_tool_specs())
    message = response["output"]["message"]
    messages.append(message)

    print(f"\n[2] Model stopped with stopReason = {response['stopReason']!r}")
    _dump("Model's raw response message", message)

    if response["stopReason"] == "tool_use":
        tool_uses = [block["toolUse"] for block in message["content"] if "toolUse" in block]

        print(f"\n[3] Model requested {len(tool_uses)} tool call(s):")
        for tu in tool_uses:
            print(f"    - {tu['name']}(**{tu['input']})  [toolUseId={tu['toolUseId']}]")

        results = await asyncio.gather(
            *(call_tool(tu["name"], tu["input"]) for tu in tool_uses)
        )

        print("\n[4] Tool execution results:")
        for tu, result in zip(tool_uses, results):
            print(f"    - {tu['name']} -> {str(result)[:200]!r}{'...' if len(str(result)) > 200 else ''}")

        tool_result_message = {
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
        messages.append(tool_result_message)

        print("\n[5] Sending tool result(s) back to the model for a final answer")
        _dump("Outgoing tool result message", tool_result_message)

        response = llm.invoke(messages, tools=get_tool_specs())
        message = response["output"]["message"]

        print(f"\n[6] Model stopped with stopReason = {response['stopReason']!r}")
        _dump("Model's final response message", message)
    else:
        print("\n[3] Model answered directly, no tool call needed.")

    final_answer = "".join(block["text"] for block in message["content"] if "text" in block)
    print(f"\n[7] Final answer: {final_answer}")
    return final_answer


async def main():
    question = input("Ask something: ")
    await run(question)


if __name__ == "__main__":
    asyncio.run(main())
