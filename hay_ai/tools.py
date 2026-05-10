import os
import subprocess
import fnmatch
import json

class AgentTools:
    """Agentic tools for reading, writing, searching code and running commands."""

    def __init__(self, workspace=None):
        self.workspace = workspace or os.getcwd()

    def schema(self):
        return [
            {"type": "function", "function": {
                "name": "read_file", "description": "Read file contents from the workspace",
                "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path (relative to workspace)"}}, "required": ["path"]}
            }},
            {"type": "function", "function": {
                "name": "write_file", "description": "Create or overwrite a file with new content",
                "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path"}, "content": {"type": "string", "description": "File content"}}, "required": ["path", "content"]}
            }},
            {"type": "function", "function": {
                "name": "edit_file", "description": "Replace a specific text snippet in a file with new content",
                "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path"}, "old_text": {"type": "string", "description": "Exact text to find and replace"}, "new_text": {"type": "string", "description": "Replacement text"}}, "required": ["path", "old_text", "new_text"]}
            }},
            {"type": "function", "function": {
                "name": "search_code", "description": "Search for a text pattern across all files in the workspace",
                "parameters": {"type": "object", "properties": {"pattern": {"type": "string", "description": "Text to search for"}, "file_glob": {"type": "string", "description": "File glob filter e.g. *.py"}}, "required": ["pattern"]}
            }},
            {"type": "function", "function": {
                "name": "list_dir", "description": "List contents of a directory",
                "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "Directory path relative to workspace", "default": "."}}}
            }},
            {"type": "function", "function": {
                "name": "run_command", "description": "Execute a shell command in the workspace directory",
                "parameters": {"type": "object", "properties": {"command": {"type": "string", "description": "Shell command"}}, "required": ["command"]}
            }},
            {"type": "function", "function": {
                "name": "analyze_project", "description": "Analyze the project structure, file types, and line counts",
                "parameters": {"type": "object", "properties": {}}
            }},
        ]

    def execute(self, name, args):
        fn = {
            "read_file": self._read_file, "write_file": self._write_file,
            "edit_file": self._edit_file, "search_code": self._search_code,
            "list_dir": self._list_dir, "run_command": self._run_command,
            "analyze_project": self._analyze_project,
        }.get(name)
        if not fn:
            return f"Unknown tool: {name}"
        try:
            return fn(**args)
        except Exception as e:
            return f"Error: {e}"

    def _resolve(self, path):
        p = os.path.normpath(os.path.join(self.workspace, path))
        if not p.startswith(os.path.normpath(self.workspace)):
            raise ValueError("Access denied: path outside workspace")
        return p

    def _read_file(self, path):
        fp = self._resolve(path)
        if not os.path.isfile(fp):
            return f"File not found: {path}"
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        if len(lines) > 500:
            return ''.join(lines[:500]) + f"\n... ({len(lines)-500} more lines truncated)"
        return ''.join(lines)

    def _write_file(self, path, content):
        fp = self._resolve(path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Written: {path} ({len(content)} chars)"

    def _edit_file(self, path, old_text, new_text):
        fp = self._resolve(path)
        if not os.path.isfile(fp):
            return f"File not found: {path}"
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        if old_text not in content:
            return f"Text not found in {path}"
        content = content.replace(old_text, new_text, 1)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Edited: {path}"

    def _search_code(self, pattern, file_glob="*"):
        results = []
        skip = {'.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next'}
        for root, dirs, files in os.walk(self.workspace):
            dirs[:] = [d for d in dirs if d not in skip]
            for fname in files:
                if not fnmatch.fnmatch(fname, file_glob):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        for i, line in enumerate(f, 1):
                            if pattern.lower() in line.lower():
                                rel = os.path.relpath(fpath, self.workspace)
                                results.append(f"{rel}:{i}: {line.rstrip()}")
                                if len(results) >= 50:
                                    return '\n'.join(results) + "\n... (50 results max)"
                except Exception:
                    continue
        return '\n'.join(results) if results else "No matches found."

    def _list_dir(self, path="."):
        fp = self._resolve(path)
        if not os.path.isdir(fp):
            return f"Not a directory: {path}"
        items = []
        for name in sorted(os.listdir(fp)):
            if name.startswith('.'):
                continue
            full = os.path.join(fp, name)
            if os.path.isdir(full):
                items.append(f"📁 {name}/")
            else:
                sz = os.path.getsize(full)
                unit = "B"
                for u in ["KB", "MB", "GB"]:
                    if sz >= 1024:
                        sz /= 1024
                        unit = u
                items.append(f"📄 {name} ({sz:.0f}{unit})")
        return '\n'.join(items) if items else "(empty)"

    def _run_command(self, command):
        try:
            r = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.workspace, timeout=60)
            out = r.stdout
            if r.stderr:
                out += f"\nSTDERR:\n{r.stderr}"
            if len(out) > 8000:
                out = out[:8000] + "\n... (truncated)"
            return out or "(no output)"
        except subprocess.TimeoutExpired:
            return "⏰ Timeout (60s limit)"
        except Exception as e:
            return f"Error: {e}"

    def _analyze_project(self):
        types = {}
        total = 0
        lines = 0
        skip = {'.git', 'node_modules', '__pycache__', 'venv', 'dist', 'build'}
        for root, dirs, files in os.walk(self.workspace):
            dirs[:] = [d for d in dirs if d not in skip]
            for f in files:
                ext = os.path.splitext(f)[1] or '(none)'
                types[ext] = types.get(ext, 0) + 1
                total += 1
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8', errors='replace') as fh:
                        lines += sum(1 for _ in fh)
                except Exception:
                    pass
        report = f"📊 Project: {os.path.basename(self.workspace)}\n"
        report += f"Files: {total} | Lines: {lines:,}\n\nFile types:\n"
        for ext, cnt in sorted(types.items(), key=lambda x: -x[1])[:15]:
            report += f"  {ext}: {cnt}\n"
        return report
