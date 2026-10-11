#!/usr/bin/env python3
"""Arabic SRT from the narration script (as spoken) and the measured scene timing.
Each scene's text is split into cues of ≤ 2 lines (≈ 42 chars per line), timed by character share."""
import json, re
from pathlib import Path

V = Path(__file__).resolve().parents[1]
js = (V / 'build/video_data.js').read_text(encoding='utf8')
T = json.loads(re.search(r'window\.T = (\[.*?\]);', js, re.S).group(1))
SCRIPT = [
    'تقرير الأداء… مبادرة سكنة وخزينة. | أداء فريق وصول للاستثمار في ركن المبادرة، ضمن معرض أكتوبر العمران 2026.',
    'مبادرة أطلقتها وزارة الإسكان والتخطيط العمراني، | تحوّل الاستفادة السكنية من استفادة واحدة… إلى استفادتين: | شقة في مدينة السلطان هيثم اليوم، | واستحقاق جديد بعد خمس سنوات من استلامها.',
    'على مدى أربعة أيام، واثنتين وخمسين ساعة تشغيل، | كان فريق وصول حاضرًا في ركن المبادرة؛ | يستقبل، ويفهم الاحتياج، ويطابق، ويوثّق.',
    'سجّل الفريق 720 عميلًا… دون أي سجل مكرر، | وجميعهم بموافقتهم على سياسة الخصوصية.',
    'بلغ الإقبال ذروته في اليوم الثاني بـ228 عميلًا، | وجاءت 44.5% من التسجيلات بعد الخامسة مساءً.',
    'وتُظهر ملاحظات المستشارين أن الطلب يميل | إلى الوحدات الأصغر… وإلى الاستثمار.',
    'ووثّق الفريق أربع عشرة صفقة، ثمانٍ منها مكتملة البيانات، | بقيمة تتجاوز أربعمئة وستة وستين ألف ريال عُماني.',
    'وتصدّر مشروع جود لطلعت مصطفى بـ58% من القيمة، | تلاه حي الوفاء للأبرار، ثم وادي صفا للأهلي صبور.',
    'تسع صفقات من أربع عشرة سُجّلت في اليوم الأخير… | فالقرار يأتي بعد المقارنة.',
    'والرحلة مستمرة: 709 عملاء في قاعدة المتابعة، | وست صفقات قيد الاستكمال.',
    'شكرًا لوزارة الإسكان والتخطيط العمراني، | وللقائمين على مبادرة سكنة وخزينة، على رؤية قرّبت الاستفادة من المواطن.',
    'الرحلة بدأت… وما زالت مستمرة. | ووصول للاستثمار مستعدة لمواصلة دعم جهود الوزارة.',
]


def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}'.replace(',1000', ',999')


def wrap(s, w=42):
    words, lines, cur = s.split(), [], ''
    for wd in words:
        if len(cur) + len(wd) + 1 > w and cur:
            lines.append(cur); cur = wd
        else:
            cur = (cur + ' ' + wd).strip()
    lines.append(cur)
    return '\n'.join(lines)


out, k = [], 1
for sc, text in zip(T, SCRIPT):
    parts = [p.strip() for p in text.split('|')]
    tot = sum(len(p) for p in parts); t = sc['v0']; span = sc['v1'] - sc['v0']
    for p in parts:
        d = span * len(p) / tot
        out.append(f'{k}\n{ts(t)} --> {ts(t + d - .05)}\n‫{wrap(p)}‬\n'); k += 1; t += d
(V / 'output').mkdir(exist_ok=True)
(V / 'output/WUSOOL_Sakna_Wa_Khazina_Performance_Motion_2026_AR.srt').write_text('\n'.join(out), encoding='utf-8-sig')
print(f'{k - 1} cues')
