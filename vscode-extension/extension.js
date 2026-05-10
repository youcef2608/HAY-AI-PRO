const vscode = require('vscode');
const http = require('http');
const https = require('https');

let panel = null;

function activate(context) {
    const serverUrl = () => vscode.workspace.getConfiguration('hay-ai').get('serverUrl', 'http://127.0.0.1:1888');

    // Chat command - opens webview panel
    context.subscriptions.push(
        vscode.commands.registerCommand('hay-ai.chat', () => {
            if (panel) { panel.reveal(); return; }

            panel = vscode.window.createWebviewPanel('hayAiChat', '🧠 HAY-AI PRO', vscode.ViewColumn.Beside, { enableScripts: true });

            panel.webview.html = getChatHTML(serverUrl());

            panel.webview.onDidReceiveMessage(async msg => {
                if (msg.type === 'send') {
                    const response = await callAPI(serverUrl(), msg.text);
                    panel.webview.postMessage({ type: 'response', content: response });
                }
            });

            panel.onDidDispose(() => { panel = null; });
        })
    );

    // Context menu commands
    const commands = {
        'hay-ai.explain': 'اشرح هذا الكود بالتفصيل:\n\n',
        'hay-ai.fix': 'أصلح الأخطاء في هذا الكود:\n\n',
        'hay-ai.review': 'راجع هذا الكود وأعطني ملاحظات لتحسينه:\n\n',
        'hay-ai.refactor': 'أعد كتابة هذا الكود بشكل أفضل وأنظف:\n\n'
    };

    for (const [cmd, prefix] of Object.entries(commands)) {
        context.subscriptions.push(
            vscode.commands.registerCommand(cmd, async () => {
                const editor = vscode.window.activeTextEditor;
                if (!editor) return;

                const selection = editor.document.getText(editor.selection);
                if (!selection) { vscode.window.showWarningMessage('حدد كوداً أولاً!'); return; }

                const prompt = prefix + '```\n' + selection + '\n```';

                await vscode.window.withProgress(
                    { location: vscode.ProgressLocation.Notification, title: '🧠 HAY-AI يفكر...' },
                    async () => {
                        const response = await callAPI(serverUrl(), prompt);
                        // Show in new document
                        const doc = await vscode.workspace.openTextDocument({ content: response, language: 'markdown' });
                        await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
                    }
                );
            })
        );
    }

    // Status bar
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '🧠 HAY-AI';
    statusBar.command = 'hay-ai.chat';
    statusBar.tooltip = 'افتح HAY-AI PRO';
    statusBar.show();
    context.subscriptions.push(statusBar);
}

function callAPI(baseUrl, prompt) {
    return new Promise((resolve, reject) => {
        const url = new URL(baseUrl + '/v1/chat/completions');
        const data = JSON.stringify({
            messages: [{ role: 'user', content: prompt }],
            max_tokens: 4096
        });

        const mod = url.protocol === 'https:' ? https : http;
        const req = mod.request(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) },
            timeout: 120000
        }, res => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const j = JSON.parse(body);
                    resolve(j.choices[0].message.content);
                } catch (e) {
                    resolve('❌ خطأ في تحليل الرد: ' + body.substring(0, 200));
                }
            });
        });

        req.on('error', e => resolve('❌ تعذر الاتصال بـ HAY-AI. تأكد أنه يعمل!\n' + e.message));
        req.on('timeout', () => { req.destroy(); resolve('⏰ انتهت مهلة الاتصال'); });
        req.write(data);
        req.end();
    });
}

function getChatHTML(serverUrl) {
    return `<!DOCTYPE html><html dir="rtl"><head>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--vscode-font-family);background:var(--vscode-editor-background);color:var(--vscode-editor-foreground);height:100vh;display:flex;flex-direction:column}
.chat{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:10px}
.msg{max-width:90%;animation:fu .3s ease}
.msg.user{align-self:flex-end;background:var(--vscode-button-background);color:var(--vscode-button-foreground);border-radius:12px 12px 4px 12px;padding:10px 14px}
.msg.ai{align-self:flex-start;background:var(--vscode-editorWidget-background);border:1px solid var(--vscode-widget-border);border-radius:12px 12px 12px 4px;padding:10px 14px}
.msg pre{background:var(--vscode-textCodeBlock-background);padding:8px;border-radius:6px;margin:6px 0;overflow-x:auto}
.iarea{padding:10px;border-top:1px solid var(--vscode-widget-border);display:flex;gap:8px}
.iarea textarea{flex:1;background:var(--vscode-input-background);color:var(--vscode-input-foreground);border:1px solid var(--vscode-input-border);border-radius:8px;padding:8px;font-family:inherit;font-size:13px;resize:none;outline:none;min-height:36px;max-height:100px}
.iarea button{background:var(--vscode-button-background);color:var(--vscode-button-foreground);border:none;border-radius:8px;padding:0 14px;cursor:pointer;font-size:16px}
.thinking{color:var(--vscode-descriptionForeground);font-size:12px;padding:4px 0}
@keyframes fu{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
</style></head><body>
<div class="chat" id="chat"></div>
<div class="iarea">
<textarea id="inp" rows="1" placeholder="اكتب رسالتك..."
onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"
oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px'"></textarea>
<button onclick="send()">➤</button>
</div>
<script>
const vscode=acquireVsCodeApi();let busy=false;
function send(){const v=inp.value.trim();if(!v||busy)return;addMsg('user',v);inp.value='';inp.style.height='auto';busy=true;
chat.insertAdjacentHTML('beforeend','<div class="thinking" id="thk">🧠 يفكر...</div>');chat.scrollTop=chat.scrollHeight;
vscode.postMessage({type:'send',text:v})}
window.addEventListener('message',e=>{const d=e.data;if(d.type==='response'){const t=document.getElementById('thk');if(t)t.remove();addMsg('ai',d.content);busy=false}});
function addMsg(r,c){const d=document.createElement('div');d.className='msg '+r;
let h=esc(c);h=h.replace(/\`\`\`(\\w*)\\n([\\s\\S]*?)\`\`\`/g,'<pre><code>$2</code></pre>');h=h.replace(/\`([^\`]+)\`/g,'<code>$1</code>');
d.innerHTML=h;chat.appendChild(d);chat.scrollTop=chat.scrollHeight}
function esc(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML}
inp.focus();
</script></body></html>`;
}

function deactivate() {}

module.exports = { activate, deactivate };
