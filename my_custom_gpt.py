import torch
import torch.nn as nn
from torch.nn import functional as F
import os
import tiktoken

# ==========================================
# 1. إعدادات العقل الجديد (Hyperparameters)
# ==========================================
batch_size = 64      # حجم دفعة ضخم (يتطلب رامات وكارت شاشة قوي)
block_size = 256     # ذاكرة خارقة (يقرأ أسطراً برمجية طويلة جداً دفعة واحدة)
learning_rate = 3e-4 # تقليل سرعة التعلم قليلاً لأن العقل أصبح ضخماً جداً ويحتاج للتركيز
device = 'cuda' if torch.cuda.is_available() else 'cpu'
n_embd = 384         # حجم تفكير مجنون (3 أضعاف السابق، لفهم الأنماط المعقدة جداً)
n_head = 6           # 6 رؤوس تفكر وتحلل الكود في نفس اللحظة
n_layer = 8          # 8 طبقات من التفكير العميق جداً

# ==========================================
# 2. بيانات التدريب (أكوادك الخاصة)
# ==========================================
# بدلاً من النص الثابت، سنقرأ الأكواد من ملف خارجي
base_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(base_dir, 'training_data.txt')

try:
    # إنشاء الملف إن لم يكن موجوداً
    if not os.path.exists(data_file):
        with open(data_file, 'w', encoding='utf-8') as f:
            f.write("def my_func():\n    pass\n")
        print(f"⚠️ تم إنشاء {data_file}. ضع أكوادك فيه ثم أعد التشغيل.")

    with open(data_file, 'r', encoding='utf-8') as f:
        text = f.read()
except Exception:
    text = "def fallback(): pass" # نص افتراضي لمنع انهيار البرنامج عند تشغيله على حاسوب آخر

# الانتقال إلى مستوى الكلمات الحقيقية (Subword Tokenization) لفهم اللغة والبرمجة معاً
# سنستخدم أداة tiktoken التي تستخدمها OpenAI لتقطيع الكلمات
enc = tiktoken.get_encoding("gpt2")
vocab_size = enc.n_vocab
encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
decode = lambda l: enc.decode(l)

data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9 * len(data))
train_data = data[:n] # 90% للتدريب
val_data = data[n:]   # 10% للاختبار

def get_batch(split):
    # استخراج عينة عشوائية من البيانات ليتعلم منها العقل
    data_split = train_data if split == 'train' else val_data
    ix = torch.randint(len(data_split) - block_size, (batch_size,))
    x = torch.stack([data_split[i:i+block_size] for i in ix])
    y = torch.stack([data_split[i+1:i+block_size+1] for i in ix])
    return x.to(device), y.to(device)

# ==========================================
# 3. هندسة العقل من الصفر (The Transformer)
# ==========================================
class Head(nn.Module):
    """رأس واحد من الانتباه الذاتي (Self-Attention)"""
    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)
        q = self.query(x)
        # حساب قوة العلاقة بين الحروف والأكواد
        wei = q @ k.transpose(-2,-1) * C**-0.5
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        v = self.value(x)
        return wei @ v

class MultiHeadAttention(nn.Module):
    """عدة رؤوس تفكر معاً في نفس الوقت"""
    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = nn.Linear(n_embd, n_embd)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.proj(out)

class FeedForward(nn.Module):
    """طبقة التفكير العميق لاستيعاب ما تم فهمه"""
    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),
        )
    def forward(self, x):
        return self.net(x)

class Block(nn.Module):
    """كتلة بناء واحدة من العقل (Transformer Block)"""
    def __init__(self, n_embd, n_head):
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MultiHeadAttention(n_head, head_size)
        self.ffwd = FeedForward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x

class MyCustomGPT(nn.Module):
    """النموذج النهائي (عقل الذكاء الاصطناعي الخاص بك)"""
    def __init__(self):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head=n_head) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_embedding_table(idx)
        pos_emb = self.position_embedding_table(torch.arange(T, device=device))
        x = tok_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)
        return logits, loss

    def generate(self, idx, max_new_tokens):
        # كيف يكتب العقل الكود بناءً على ما تعلمه
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -block_size:]
            logits, loss = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

# ==========================================
# 4. بدء التدريب وولادة العقل
# ==========================================
if __name__ == "__main__":
    print("جاري بناء العقل الجديد الخاص بك من الصفر... 🧠")
    model = MyCustomGPT().to(device)
    
    # التحقق من وجود عقل سابق لإكمال التدريب (Train More)
    brain_path = os.path.join(base_dir, 'my_own_brain.pth')
    if os.path.exists(brain_path):
        try:
            model.load_state_dict(torch.load(brain_path, map_location=device, weights_only=True))
            print("✅ تم تحميل العقل بنجاح لإكمال التدريب وزيادة ذكائه...")
        except Exception as e:
            print("⚠️ لقد قمت بتكبير حجم العقل (أبعاد مجنونة)! لذلك سيبدأ هذا العقل كطفل جديد بقدرات استيعاب مرعبة...")
            print("جاري التدريب من الصفر بالقدرات الجديدة...")

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    print(f"بدء التدريب المستمر (إلى ما لا نهاية) على {device.upper()}... (لإيقاف التدريب اضغط Ctrl+C)")
    iter_count = 0
    while True:
        xb, yb = get_batch('train')
        logits, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        
        if iter_count % 100 == 0:
            print(f"الجولة {iter_count}: نسبة الغباء/الخطأ = {loss.item():.4f}")
            
        # حفظ العقل بشكل دوري كل 500 جولة حتى لا يضيع تعبه
        if iter_count > 0 and iter_count % 500 == 0:
            torch.save(model.state_dict(), brain_path)
            print("💾 تم حفظ خبرات العقل! مستمر في المذاكرة والتدريب...")
            
        iter_count += 1

    # ==========================================
    # 5. اختبار ذكاء العقل الجديد
    # ==========================================
    print("\n--- اختبار كتابة الكود ---")
    # نعطيه حرف بداية فارغ ليقوم هو بتأليف الكود من خياله بناءً على ما تعلمه
    context = torch.zeros((1, 1), dtype=torch.long, device=device)
    generated_indices = model.generate(context, max_new_tokens=150)[0].tolist()
    
    print(decode(generated_indices))