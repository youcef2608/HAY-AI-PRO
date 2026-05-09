import torch
import sys
import os

# استيراد هندسة العقل وأدوات التشفير من ملفك الأصلي
sys.path.append('h:\\HAY-AI-PRO')
from my_custom_gpt import MyCustomGPT, encode, decode, device

print("🚀 جاري إيقاظ العقل المجنون...")

# تهيئة الجمجمة (النموذج) وتحميل الذكريات
model = MyCustomGPT().to(device)

# تحديد مسار العقل بذكاء (ليعمل كسكربت أو كبرنامج exe جاهز في حاسوب آخر)
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
brain_path = os.path.join(base_dir, 'my_own_brain.pth')

try:
    model.load_state_dict(torch.load(brain_path, map_location=device, weights_only=True))
    print("✅ تم استرجاع ذكريات وخبرات العقل المجنون بنجاح!")
except Exception as e:
    print(f"❌ لم يتم العثور على الذكريات في المسار: {brain_path}")
    print("يرجى التأكد من وضع ملف 'my_own_brain.pth' بجانب البرنامج مباشرة!")
    sys.exit()

model.eval() # تفعيل وضع الاختبار (لا يتعلم هنا، بل يطبق ما تعلمه فقط)

print("\n" + "="*50)
print("🔥 العقل المجنون جاهز الآن! 🔥")
print("اكتب بداية أي كود وسيقوم هو بإكماله لك (أو اكتب 'خروج' للإغلاق)")
print("="*50)

while True:
    prompt = input("\nأنت (اكتب كوداً): ")
    if prompt.strip() == 'خروج':
        break
        
    input_ids = encode(prompt)
    if len(input_ids) == 0:
        context = torch.zeros((1, 1), dtype=torch.long, device=device)
    else:
        context = torch.tensor([input_ids], dtype=torch.long, device=device)

    print("العقل المجنون يكتب... 🧠💻\n")
    with torch.no_grad():
        generated_indices = model.generate(context, max_new_tokens=300)[0].tolist()
        
    print(decode(generated_indices))