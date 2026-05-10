import os
import json
from pathlib import Path

class Config:
    """HAY-AI Configuration - 100% Local, No API Keys."""

    DEFAULT = {
        "ollama_url": "http://localhost:11434",
        "model": "qwen2.5-coder:7b",
        "server": {"host": "127.0.0.1", "port": 1888},
        "agent": {"max_iterations": 15, "workspace": ""},
        "models_available": []
    }

    def __init__(self):
        self.config_dir = Path.home() / ".hay-ai"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load()

    def _load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                merged = json.loads(json.dumps(self.DEFAULT))
                merged.update(saved)
                return merged
            except Exception:
                pass
        return json.loads(json.dumps(self.DEFAULT))

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    @property
    def ollama_url(self):
        return self.config["ollama_url"]

    @property
    def model(self):
        return self.config["model"]

    @model.setter
    def model(self, value):
        self.config["model"] = value
