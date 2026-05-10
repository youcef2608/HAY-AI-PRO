import httpx
import json
import os

class OllamaProvider:
    def __init__(self, config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=300.0)

    async def chat(self, messages, tools=None, stream=False):
        body = {"model": self.config.model, "messages": messages, "stream": stream}
        if tools: body["tools"] = tools
        r = await self.client.post(f"{self.config.ollama_url}/api/chat", json=body, timeout=300.0)
        return r.json()

class GroqProvider:
    def __init__(self, config):
        self.config = config
        self.api_key = config.groq_api_key
        self.client = httpx.AsyncClient(timeout=300.0)

    async def chat(self, messages, tools=None, stream=False):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        body = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.7}
        r = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
        return r.json()

def get_provider(config):
    if config.provider == "groq": return GroqProvider(config)
    return OllamaProvider(config)
