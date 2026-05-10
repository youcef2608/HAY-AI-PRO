import httpx
import json

class OllamaProvider:
    """100% Local LLM via Ollama - No API keys, No internet needed."""

    def __init__(self, config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=300.0)

    @property
    def base_url(self):
        return self.config.ollama_url

    async def is_running(self):
        """Check if Ollama is running."""
        try:
            r = await self.client.get(f"{self.base_url}/api/version")
            return r.status_code == 200
        except Exception:
            return False

    async def list_models(self):
        """List locally installed models."""
        try:
            r = await self.client.get(f"{self.base_url}/api/tags")
            r.raise_for_status()
            data = r.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    async def pull_model(self, model_name, on_progress=None):
        """Download a model. Streams progress."""
        async with self.client.stream(
            "POST", f"{self.base_url}/api/pull",
            json={"name": model_name}, timeout=None
        ) as resp:
            async for line in resp.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        if on_progress:
                            on_progress(data)
                    except json.JSONDecodeError:
                        pass

    async def chat(self, messages, tools=None, stream=False):
        """Send chat request to Ollama with optional tool calling."""
        body = {
            "model": self.config.model,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": 0.7, "num_predict": 4096}
        }

        if tools:
            body["tools"] = tools

        if stream and not tools:
            return self._stream(body)
        
        r = await self.client.post(
            f"{self.base_url}/api/chat", json=body, timeout=300.0
        )
        r.raise_for_status()
        result = r.json()

        # Convert to OpenAI-like format for compatibility
        msg = result.get("message", {})
        tool_calls = msg.get("tool_calls")
        
        openai_msg = {"role": "assistant", "content": msg.get("content", "")}
        
        if tool_calls:
            openai_tc = []
            for i, tc in enumerate(tool_calls):
                fn = tc.get("function", {})
                openai_tc.append({
                    "id": f"call_{i}",
                    "type": "function",
                    "function": {
                        "name": fn.get("name", ""),
                        "arguments": json.dumps(fn.get("arguments", {}))
                    }
                })
            openai_msg["tool_calls"] = openai_tc
            openai_msg["content"] = openai_msg["content"] or None

        return {
            "choices": [{
                "message": openai_msg,
                "finish_reason": "tool_calls" if tool_calls else "stop"
            }]
        }

    async def _stream(self, body):
        """Stream response tokens."""
        async with self.client.stream(
            "POST", f"{self.base_url}/api/chat", json=body, timeout=300.0
        ) as resp:
            async for line in resp.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

    async def close(self):
        await self.client.aclose()
