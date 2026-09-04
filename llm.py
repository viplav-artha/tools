import os

import boto3
from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    return value.strip()


def _env_float(name: str, default: float) -> float:
    value = _env(name)
    if value in (None, ""):
        return default
    return float(value)


class BedrockLLM:
    def __init__(self, client, model_id: str, temperature: float):
        self._client = client
        self.model_id = model_id
        self.temperature = temperature

    def invoke(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        request = {
            "modelId": self.model_id,
            "messages": messages,
            "inferenceConfig": {"temperature": self.temperature},
        }
        if tools:
            request["toolConfig"] = {"tools": tools}

        return self._client.converse(**request)


def get_llm() -> BedrockLLM:
    model_id = _env("BEDROCK_CHAT_MODEL_ID", "us.amazon.nova-pro-v1:0")
    region = _env("BEDROCK_REGION") or _env("AWS_REGION", "us-east-1")
    profile = _env("AWS_PROFILE", "Artha-stg-dev")
    temperature = _env_float("LLM_TEMPERATURE", 0)

    if not model_id:
        raise ValueError("BEDROCK_CHAT_MODEL_ID not configured")
    if not region:
        raise ValueError("BEDROCK_REGION or AWS_REGION not configured")

    # credentials_profile_name equivalent: boto3 Session picks up your active AWS SSO profile
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    client = session.client("bedrock-runtime", region_name=region)

    return BedrockLLM(client=client, model_id=model_id, temperature=temperature)
