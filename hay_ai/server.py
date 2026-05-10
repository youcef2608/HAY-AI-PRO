import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from .config import Config
from .agent import Agent

config = Config()
agent = Agent(config)
app = FastAPI(title="HAY-AI PRO", version="1.0.0")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    max_tokens: Optional[int] = 4096
    model: Optional[str] = None
    stream: Optional[bool] = False

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    prompt = req.messages[-1].content
    if req.model:
        config.config["model"] = req.model
    response = await agent.run(prompt)
    return {
        "id": "hay-ai", "object": "chat.completion", "model": config.model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": response}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

@app.get("/v1/models")
async def list_models():
    models = await agent.provider.list_models()
    return {"object": "list", "data": [{"id": m, "object": "model", "owned_by": "local"} for m in models]}

@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            msg = data.get("message", "")
            workspace = data.get("workspace", "")
            if workspace:
                agent.set_workspace(workspace)
            if data.get("action") == "clear":
                agent.clear_history()
                await ws.send_json({"type": "cleared"})
                continue
            def on_tool(name, args):
                asyncio.get_event_loop().create_task(ws.send_json({"type": "tool", "name": name, "args": args}))
            response = await agent.run(msg, on_tool=on_tool)
            await ws.send_json({"type": "response", "content": response})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "content": str(e)})
        except:
            pass

@app.get("/api/status")
async def status():
    running = await agent.provider.is_running()
    models = await agent.provider.list_models() if running else []
    return {"ollama_running": running, "current_model": config.model, "models": models, "workspace": agent.tools.workspace}

@app.post("/api/config")
async def update_config(data: dict):
    if "model" in data:
        config.config["model"] = data["model"]
    if "workspace" in data:
        config.config["agent"]["workspace"] = data["workspace"]
        agent.set_workspace(data["workspace"])
    config.save()
    return {"status": "ok"}

@app.post("/api/pull-model")
async def pull_model(data: dict):
    model_name = data.get("model", "qwen2.5-coder:1.5b")
    try:
        await agent.provider.pull_model(model_name)
        return {"status": "ok", "model": model_name}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
