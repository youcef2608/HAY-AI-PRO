import json
from .tools import AgentTools
from .providers import OllamaProvider

SYSTEM_PROMPT = """You are **HAY-AI**, an elite AI coding agent. You run 100% locally on the user's machine. You have direct access to the codebase through powerful tools.

## Your Tools:
- **read_file(path)**: Read any file in the workspace
- **write_file(path, content)**: Create or overwrite files  
- **edit_file(path, old_text, new_text)**: Surgically edit specific parts of a file
- **search_code(pattern, file_glob)**: Find patterns across the entire codebase
- **list_dir(path)**: Explore directory structure
- **run_command(command)**: Execute shell commands (build, test, git, npm, pip, etc.)
- **analyze_project()**: Get full project overview

## Rules:
1. ALWAYS read relevant files before making changes
2. Use tools proactively to understand context before answering
3. Write complete, production-quality code - never use placeholders like "..."
4. Use edit_file for small changes, write_file for new/full rewrites
5. After writing code, run commands to test when appropriate
6. Support Arabic and English

You are HAY-AI - a powerful local AI coding assistant. 🚀"""


class Agent:
    """HAY-AI Agent with tool-calling loop."""

    def __init__(self, config, workspace=None):
        self.config = config
        self.provider = OllamaProvider(config)
        ws = workspace or config.config.get("agent", {}).get("workspace") or "."
        self.tools = AgentTools(ws)
        self.max_iter = config.config.get("agent", {}).get("max_iterations", 15)
        self.history = []

    async def run(self, user_message, on_tool=None, on_stream=None):
        """Run agent loop. Returns final response text."""
        self.history.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history[-20:]  # Keep last 20 messages
        tool_schemas = self.tools.schema()

        for _ in range(self.max_iter):
            try:
                result = await self.provider.chat(messages, tools=tool_schemas)
            except Exception as e:
                error_msg = f"❌ Error: {e}"
                self.history.append({"role": "assistant", "content": error_msg})
                return error_msg

            msg = result["choices"][0]["message"]
            messages.append(msg)

            tool_calls = msg.get("tool_calls")
            if not tool_calls:
                content = msg.get("content", "")
                self.history.append({"role": "assistant", "content": content})
                return content

            # Execute tools
            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"]["arguments"]) if isinstance(tc["function"]["arguments"], str) else tc["function"]["arguments"]
                except (json.JSONDecodeError, TypeError):
                    fn_args = {}

                if on_tool:
                    on_tool(fn_name, fn_args)

                result_text = self.tools.execute(fn_name, fn_args)
                messages.append({
                    "role": "tool",
                    "content": str(result_text)
                })

        final = "⚠️ Max iterations reached."
        self.history.append({"role": "assistant", "content": final})
        return final

    def set_workspace(self, path):
        self.tools = AgentTools(path)

    def clear_history(self):
        self.history = []

    async def close(self):
        await self.provider.close()
