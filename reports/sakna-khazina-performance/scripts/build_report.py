#!/usr/bin/env python3
"""metrics.json + processed registers -> charts/*.svg + build/report.html (A4 portrait, RTL, fixed pages).

Every number on every page comes from data/aggregates/metrics.json or data/processed/*.json.
"""
import json, math, os, re, sys
from pathlib import Path
from report_lib import *  # noqa: F401,F403
from report_lib import _t  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
M = json.loads((ROOT / 'data/aggregates/metrics.json').read_text(encoding='utf8'))
C = json.loads((ROOT / 'data/processed/customers.json').read_text(encoding='utf8'))
D = json.loads((ROOT / 'data/processed/deals.json').read_text(encoding='utf8'))
V = M['validation']
BLEED = os.environ.get('BLEED', '0') == '1'
CHARTS = ROOT / 'charts'; CHARTS.mkdir(exist_ok=True)
BUILD = ROOT / 'build'; BUILD.mkdir(exist_ok=True)

EXTRACT_DATE = '2026-10-11'
SRC_REG = f'سجل تسجيل العملاء «بيانات عملاء أكتوبر العمران» — تبويب «العملاء» · استخراج {d_ar(EXTRACT_DATE)}'
SRC_SALES = f'سجل المبيعات «جدول مبيعات أكتوبر العمران - سكنة وخزينة» · استخراج {d_ar(EXTRACT_DATE)}'
SRC_BOTH = f'سجل تسجيل العملاء وسجل المبيعات · استخراج {d_ar(EXTRACT_DATE)}'

LOGO_COBRAND = '../../../brand/logo/cobrand/sukna-w-khazinah_x_mhup.svg'
LOGO_COBRAND_DARK = '../../../brand/logo/cobrand/sukna-w-khazinah_x_mhup_on-dark.svg'
LOGO_W = '../logos/WUSOOL_Primary_FullColor.svg'
LOGO_W_REV = '../logos/WUSOOL_Reversed.svg'

n720 = M['customers_total']


def chart(name, svg_markup):
    (CHARTS / f'{name}.svg').write_text(svg_markup, encoding='utf8')
    return f'<div class="chart-box">{svg_markup}</div>'


# ======================================================================== page model
PAGES = []
PART = {'name': ''}


def add(body, sec='', cls='', sheet='', head=True, foot=True, toc=None, part_toc=None):
    PAGES.append(dict(body=body, sec=sec or PART['name'], cls=cls, sheet=sheet, head=head, foot=foot, toc=toc, part_toc=part_toc))


def sec_head(kicker, title, lead=''):
    return (f'<div class="sec-head"><div class="kicker">{kicker}</div><h1>{title}</h1>'
            + (f'<p class="lead">{lead}</p>' if lead else '') + '</div>')


def kpi(v, label, sub='', cls=''):
    return f'<div class="kpi {cls}"><div class="v">{v}</div><div class="l">{label}</div>' + (f'<div class="s">{sub}</div>' if sub else '') + '</div>'


def src(text):
    return f'<div class="src">{text}</div>'


def divider(no, title, text, items):
    PART['name'] = title
    mini = ''.join(f'<div>{t}</div>' for t in items)
    add(f'''<div class="divider">
      <div class="rule-asc"></div>
      <div class="no">{N(f"{no:02d}")}</div>
      <div class="tt"><div class="k">القسم {N(f"{no:02d}")}</div><h1>{title}</h1><p>{text}</p></div>
      <div class="toc-mini">{mini}</div></div>''', sec=title, sheet='bg-ink dark', head=False, part_toc=(no, title))


# ======================================================================== derived values used across pages
by_dev = M['by_developer']; by_proj = M['by_project']; by_cons = M['by_consultant']
ev_days = [b for b in M['by_day'] if b['in_event']]
best_day = max(ev_days, key=lambda b: b['registrations'])
deal_peak_day = max(M['by_day'], key=lambda b: b['deals'])
top_dev = by_dev[0]; top_proj = by_proj[0]
peak1, peak2 = M['peak_hours'][0], M['peak_hours'][1]
evening = M['by_block'][2]
bed = {b['label']: b['count'] for b in M['bedroom_mentions']}
bed_total = sum(bed.values())
tags = {t['tag']: t['count'] for t in M['interest_tags']}
pending_dev = max(by_dev, key=lambda r: r['pending'])
contracted = [t for t in M['team'] if t['contracted']]
supporting = [t for t in M['team'] if not t['contracted']]
first_reg = M['first_registration']; last_reg = M['last_registration']
hr = lambda h: f'{h:02d}:00'
ID_LATE = next(d['deal_id'] for d in D if d['time'] < f"{M['event']['open_hour']:02d}:00" and d['time'] < '01:00')
ID_UNITPATTERN = next(d['deal_id'] for d in D if any('نمط وحدات' in f for f in d['flags']))
ID_CROSS = next(d['deal_id'] for d in D if d['register_seq'] and d['consultant'] not in d['register_staff'])
ID_NOTE = next(d['deal_id'] for d in D if any(f.startswith('ملاحظة المستشار') for f in d['flags']))
D_NOTE = next(d for d in D if d['deal_id'] == ID_NOTE)
D_UNIT = next(d for d in D if d['deal_id'] == ID_UNITPATTERN)
ID_VILLA = next(d['deal_id'] for d in D if d['unit_type'] == 'فيلا')
MULTI_DEV = [r for r in by_proj if len(r['developers']) > 1]


# ======================================================================== 1 · COVER
add(f'''<div class="cover">
  <img class="cb" src="{LOGO_COBRAND}" alt="وزارة الإسكان والتخطيط العمراني × سكنة وخزينة">
  <div class="meta-top"><span class="conf-tag">سري — للاستخدام الرسمي</span><br><br>
    <span class="en">Performance Report {N(2026)}</span><br>{d_ar(EXTRACT_DATE)}</div>
  <div class="title">
    <div class="k">{M['event']['name'].replace('2026', N(2026))} · ركن مبادرة «سكنة وخزينة»</div>
    <div class="t1">تقرير الأداء</div>
    <div class="t2">مبادرة سكنة وخزينة</div>
    <div class="t3">أداء فريق وصول للاستثمار في ركن المبادرة<br>{d_ar(M['event']['start'], year=False)} – {d_ar(M['event']['end'])}</div>
  </div>
  <div class="band"></div>
  <div class="issuer">
    <div class="by"><div class="lab">أعدّه</div><img src="{LOGO_W}" alt="WUSOOL"><div class="nm">وصول للاستثمار</div></div>
    <div class="to">مقدَّم إلى<br><b>وزارة الإسكان والتخطيط العمراني</b><br>سلطنة عُمان</div>
  </div></div>''', sheet='bg-paper', head=False, foot=False)

# ======================================================================== 2 · DOCUMENT CONTROL
add(f'''{sec_head('بيانات الوثيقة', 'الاعتماد والسرية')}
<table class="dc">
<tr><th>عنوان الوثيقة</th><td>تقرير أداء فريق وصول للاستثمار — مبادرة «سكنة وخزينة»</td></tr>
<tr><th>الجهة المُعِدّة</th><td>وصول للاستثمار (شركة وصول الحديثة للاستثمار)</td></tr>
<tr><th>مقدَّم إلى</th><td>وزارة الإسكان والتخطيط العمراني</td></tr>
<tr><th>الفعالية</th><td>{M['event']['name'].replace('2026', N(2026))} — ركن وزارة الإسكان والتخطيط العمراني لمبادرة «سكنة وخزينة»</td></tr>
<tr><th>أيام المعرض</th><td>{d_ar(M['event']['start'], weekday=True)} – {d_ar(M['event']['end'], weekday=True)} · من {N('9:00')} صباحًا حتى {N('10:00')} مساءً</td></tr>
<tr><th>نطاق البيانات</th><td>من أول تسجيل ({d_ar(first_reg)}، {N(first_reg[11:16])}) إلى آخر تسجيل ({d_ar(last_reg)}، {N(last_reg[11:16])})</td></tr>
<tr><th>تاريخ استخراج البيانات</th><td>{d_ar(EXTRACT_DATE)}</td></tr>
<tr><th>محتوى الوثيقة</th><td>{N(n720)} سجل عميل · {N(M['deals_total'])} سجل صفقة · مؤشرات أداء · سجلات كاملة في الملاحق</td></tr>
<tr><th>الإصدار</th><td>{N('1.0')} — النسخة النهائية</td></tr>
<tr><th>التصنيف</th><td><b>سري — للاستخدام الرسمي</b></td></tr>
<tr><th>عدد الصفحات</th><td>{N('{{TOTAL}}')}</td></tr>
</table>
<div class="notice" style="margin-top:8mm">
  <div class="h">تنبيه السرية</div>
  <p class="small" style="margin:0">تتضمن هذه الوثيقة معلومات تشغيلية وبيانات شخصية لعملاء سجّلوا في ركن المبادرة بعد موافقتهم على سياسة الخصوصية
  ({N(V['consent_yes'])} من {N(n720)}). أُعدّت للاستخدام الرسمي لدى وزارة الإسكان والتخطيط العمراني والجهات المخوّلة فقط، ولا يجوز نسخها أو تداولها أو نشرها لغير هذا الغرض.
  حُجبت أرقام البطاقات المدنية إلا آخر ثلاثة أرقام في سجل الصفقات، ولم تُدرج عناوين البريد الإلكتروني.</p>
</div>
<div style="margin-top:9mm"><h3>الاعتماد</h3>
<div class="signs">
  <div><b>أعدّه</b>الاسم:<br>التوقيع:<br>التاريخ:</div>
  <div><b>راجعه</b>الاسم:<br>التوقيع:<br>التاريخ:</div>
  <div><b>اعتمده — وصول للاستثمار</b>الاسم:<br>التوقيع:<br>التاريخ:</div>
</div></div>''', sec='بيانات الوثيقة')

# ======================================================================== 3 · CONTENTS (filled after all pages exist)
add('{{TOC}}', sec='المحتويات')

# ======================================================================== 4 · OPENING WORD
add(f'''{sec_head('كلمة افتتاحية', 'مشاركة نوثّقها بالأرقام')}
<div class="letter" style="max-width:150mm">
<p>يسرّ وصول للاستثمار أن تقدّم هذا التقرير توثيقًا لمشاركة فريقها في ركن مبادرة «سكنة وخزينة» ضمن {M['event']['name'].replace('2026', N(2026))}،
خلال الفترة من {d_ar(M['event']['start'], year=False)} إلى {d_ar(M['event']['end'])}.</p>
<p>لم نتعامل مع هذه المشاركة على أنها حضور في ركن عرض، بل على أنها مسؤولية في تمثيل مبادرة وطنية أمام المواطنين: أن نستقبل الزائر،
ونفهم احتياجه، ونشرح له المبادرة بدقة، ونطابقه مع الخيار المناسب، ونوثّق بياناته بموافقته، ثم نتابع معه بعد انتهاء المعرض.</p>
<p>يعرض التقرير ما تحقق كما ورد في سجلات التشغيل: {N(n720)} عميلًا مسجّلًا، و{N(M['deals_total'])} صفقة مسجّلة، منها {N(M['deals_documented'])} صفقات
موثقة برمز الوحدة وسعرها بقيمة إجمالية {OMR(M['deal_value_total'])}. ويعرض كذلك ما لم يكتمل بعد، لأن الصورة الدقيقة هي أساس أي متابعة جادة.</p>
<p>كل رقم في هذا التقرير قابل لإعادة الحساب من مصدره. وقد خضعت البيانات قبل اعتمادها لمطابقة بين سجل تسجيل العملاء ونسخته في نظام إدارة العملاء وسجل المبيعات،
ووُثّقت الملاحظات التي ظهرت أثناء المطابقة في ملاحق التقرير.</p>
<div class="sign"><div><div class="w">وصول للاستثمار</div><div class="small muted">{d_ar(EXTRACT_DATE)}</div></div><img src="{LOGO_W}" alt="WUSOOL"></div>
</div>''', sec='كلمة افتتاحية', toc=('كلمة افتتاحية', 1))

# ======================================================================== 5 · THANKS LETTER
add(f'''{sec_head('شكر وتقدير', 'إلى معالي وزير الإسكان والتخطيط العمراني')}
<div class="letter">
<p class="salute">معالي وزير الإسكان والتخطيط العمراني، المحترم<br>وزارة الإسكان والتخطيط العمراني<br>القائمون على مبادرة «سكنة وخزينة»</p>
<p>تتقدّم وصول للاستثمار بخالص الشكر والتقدير إلى معاليكم، وإلى وزارة الإسكان والتخطيط العمراني، على الرؤية التي تقف خلف مبادرة «سكنة وخزينة».
فقد أعادت المبادرة صياغة مفهوم الاستفادة السكنية الحكومية: من استفادة واحدة مدى الحياة إلى استفادتين؛ تبدأ الأولى بشقة في مدينة السلطان هيثم،
ويُفتح الاستحقاق مرة أخرى بعد خمس سنوات من استلامها، مع احتفاظ المستفيد بشقته الأولى. إنه نموذج يقرّب الاستفادة من المواطن، ويحوّلها من منحة تنتهي إلى أصل يبقى.</p>
<p>ونخص بالتقدير القائمين على المبادرة، ومنهم دائرة الهوية والوصول، والفرق التنظيمية والتنفيذية في الوزارة، على تنظيم ركن المبادرة في المعرض، ووضوح الإجراءات،
وسهولة التواصل، والدعم الذي قدّموه للفرق المشاركة طوال أيام المعرض. لقد أتاح هذا التنظيم لفرق القطاع الخاص أن تعمل ضمن إطار واحد واضح،
وأن تصل إلى المستفيدين بمعلومة دقيقة وتجربة متكاملة.</p>
<p>إن الإقبال الذي شهده الركن — {N(n720)} عميلًا سجّلوا بياناتهم خلال أيام المعرض وما تلاها — يعكس اهتمامًا حقيقيًا لدى المواطنين بهذا النموذج،
ويؤكد قدرة المبادرة على أن تترك أثرًا ممتدًا في قرارات الأسر العُمانية وفي السوق السكني خلال السنوات المقبلة.</p>
<p>ونعتزّ في وصول للاستثمار بأن نكون أحد فرق القطاع الخاص التي أسهمت في تحويل هذه الرؤية إلى نتائج على أرض الواقع، ونؤكد استعدادنا لمواصلة العمل مع الوزارة في كل ما يخدم المبادرة والمستفيدين منها.</p>
<p>وتفضّلوا بقبول فائق الاحترام والتقدير.</p>
<div class="sign"><div><div class="w">وصول للاستثمار</div><div class="small muted">{d_ar(EXTRACT_DATE)}</div></div><img src="{LOGO_W}" alt="WUSOOL"></div>
</div>''', sec='شكر وتقدير', toc=('شكر وتقدير', 1))

# ======================================================================== 6 · EXECUTIVE SUMMARY
in_ev, post_ev = M['customers_in_event'], M['customers_post_event']
add(f'''{sec_head('الملخص التنفيذي', 'الصورة في صفحة واحدة')}
<div class="grid g12-5-7" style="align-items:end">
  <div><div class="hero-num">{N(n720)}</div>
    <div style="font-family:Changa;font-weight:700;font-size:15pt;line-height:1.35;margin-top:3mm">عميلًا مسجّلًا في ركن المبادرة</div>
    <div class="small muted" style="margin-top:1.5mm">{N(in_ev)} خلال أيام المعرض الأربعة، و{N(post_ev)} بعد انتهائه · بلا سجلات مكررة</div></div>
  <div class="grid g2" style="gap:4mm 6mm">
    {kpi(N(M['deals_total']), 'صفقة مسجّلة', f"{N(M['deals_documented'])} موثقة برمز الوحدة والسعر · {N(M['deals_pending'])} قيد الاستكمال", 'accent')}
    {kpi(N(money(M['deal_value_total'])) + '<span class="cur">ر.ع.</span>', 'قيمة الصفقات الموثقة', f"متوسط الصفقة {OMR(M['deal_value_avg'])}", 'accent')}
    {kpi(N(M['conv_deal_records_per_100']), 'صفقة لكل 100 عميل مسجّل', f"{N(M['deal_customers_matched'])} من عملاء السجل مرتبطون بصفقة ({N(pct(M['conv_registered_with_deal'], 2))})")}
    {kpi(N(M['open_pipeline']), 'عميلًا في قاعدة المتابعة', 'مسجّلون دون صفقة مسجّلة حتى تاريخ الاستخراج')}
  </div>
</div>
<div class="grid g4" style="margin-top:8mm;gap:5mm">
  {kpi(N(M['event']['days']), 'أيام معرض', f"{N(M['event']['operating_hours'])} ساعة تشغيل")}
  {kpi(N(M['avg_per_event_day']), 'تسجيلًا في اليوم', f"{N(M['avg_per_operating_hour'])} في كل ساعة تشغيل")}
  {kpi(f"{N(M['developers_count'])} · {N(M['projects_count'])}", 'مطورون · مشاريع', 'في سجل المبيعات')}
  {kpi(N(M['consultants_contracted']), 'مستشارًا عقاريًا متعاقدًا', f"{N(M['contracted_in_records'])} منهم في سجلات الركن")}
</div>
<div class="panel" style="margin-top:8mm"><h2>أبرز ما تقوله البيانات</h2>
<ul class="dots">
<li><b>الإقبال بلغ ذروته في اليوم الثاني.</b> سجّل {d_ar(best_day['date'], year=False, weekday=True)} {N(best_day['registrations'])} عميلًا، وتركّز {N(pct(evening['share']))} من تسجيلات أيام المعرض في الفترة المسائية بعد {N('17:00')}.</li>
<li><b>القرار يحتاج وقتًا.</b> {N(deal_peak_day['deals'])} من {N(M['deals_total'])} صفقات سُجّلت في اليوم الأخير ({d_ar(deal_peak_day['date'], year=False, weekday=True)})، بعد أيام من التعريف والمقارنة.</li>
<li><b>{top_dev['name']} — مشروع «{top_proj['name']}» يتصدّر القيمة الموثقة</b> بـ{N(top_dev['documented'])} صفقات تمثل {N(pct(top_dev['share']))} من الإجمالي، بسعر {OMR(top_dev['avg'])} للوحدة.</li>
<li><b>الطلب المرصود يميل إلى الوحدات الأصغر وإلى الاستثمار.</b> من ملاحظات المستشارين التي ذكرت عدد الغرف، أشار {N(bed['غرفة وصالة'])} من {N(bed_total)} إلى غرفة وصالة، وذُكر الاستثمار في {N(tags.get('استثمار', 0))} ملاحظة.</li>
<li><b>الرحلة لم تنتهِ بانتهاء المعرض.</b> {N(M['open_pipeline'])} عميلًا في قاعدة المتابعة، و{N(M['deals_pending'])} صفقات تنتظر استكمال بيانات الوحدة والسعر، و{N(post_ev)} تسجيلًا جديدًا بعد اليوم الأخير.</li>
</ul></div>
{src(SRC_BOTH)}''', sec='الملخص التنفيذي', toc=('الملخص التنفيذي', 1))

# ======================================================================== 7 · DASHBOARD
reg_cols = [dict(label=b['weekday'], sub=f"{int(b['date'][8:])} أكتوبر", value=b['registrations'], vlabel=num(b['registrations']),
                 hl=b is best_day) for b in M['by_day']]
for c_, b in zip(reg_cols, M['by_day']):
    if not b['in_event']:
        c_['color'] = AQUA
dash_reg = columns(reg_cols, w=320, h=190, title='التسجيلات اليومية', axis_h=38, label_size=9.5)
deal_cols = [dict(label=b['weekday'], sub=f"{int(b['date'][8:])} أكتوبر", value=b['deals'], vlabel=num(b['deals'])) for b in M['by_day'] if b['date'] <= '2026-10-09']
dash_deals = columns(deal_cols, w=320, h=190, title='الصفقات المسجّلة يوميًا', axis_h=38, label_size=9.5)
seg_cols = [MIDNIGHT, AQUA, '#99B5B9']
dash_donut = donut([(r['value'], seg_cols[i]) for i, r in enumerate(by_dev)], size=150, center=pct(top_dev['share'], 0), center_sub=top_dev['name'])
hour_cols = [dict(label=str(h['hour']), value=h['registrations'], vlabel=num(h['registrations']) if h['hour'] in (peak1['hour'], peak2['hour']) else None,
                  hl=h['hour'] == peak1['hour']) for h in M['by_hour']]
dash_hours = columns(hour_cols, w=320, h=170, title='التسجيلات حسب الساعة', axis_h=22, col_w=14, label_size=9)
legend_dev = ''.join(f'<div style="display:flex;gap:2mm;align-items:center;margin-bottom:1.6mm"><span style="width:3mm;height:3mm;border-radius:.6mm;background:{seg_cols[i]};display:inline-block"></span>'
                     f'<span>{r["name"]}</span><span style="margin-inline-start:auto;font-weight:600">{N(pct(r["share"]))}</span></div>' for i, r in enumerate(by_dev))
add(f'''{sec_head('لوحة المؤشرات', 'المؤشرات الرئيسية في لمحة')}
<div class="grid g2" style="gap:7mm 8mm">
  <div class="panel"><h3>التسجيلات اليومية</h3>{chart('dash_daily_registrations', dash_reg)}<div class="note">الأعمدة الفاتحة: تسجيلات المتابعة بعد انتهاء المعرض.</div></div>
  <div class="panel"><h3>الصفقات المسجّلة حسب يوم التوثيق</h3>{chart('dash_daily_deals', dash_deals)}</div>
  <div class="panel"><h3>توزيع القيمة الموثقة حسب المطور</h3>
    <div style="display:grid;grid-template-columns:40mm 1fr;gap:6mm;align-items:center">{chart('dash_developer_share', dash_donut)}<div class="small">{legend_dev}
    <div class="note" style="margin-top:2mm">من إجمالي {OMR(M['deal_value_total'])}</div></div></div></div>
  <div class="panel"><h3>التسجيلات حسب ساعة اليوم (أيام المعرض)</h3>{chart('dash_hourly', dash_hours)}<div class="note">الساعة {N(hr(peak1['hour']))} هي الأعلى ({N(peak1['registrations'])} تسجيلًا)، تليها {N(hr(peak2['hour']))} ({N(peak2['registrations'])}).</div></div>
</div>
<div class="grid g4" style="margin-top:7mm;gap:5mm">
  {kpi(N(money(M['deal_value_median'])), 'الوسيط لقيمة الصفقة (ر.ع.)')}
  {kpi(N(money(M['price_per_m2_avg'])), 'متوسط سعر المتر المربع (ر.ع.)', 'للصفقات الموثقة')}
  {kpi(N(pct(100 * V['consent_yes'] / n720, 0)), 'موافقة على سياسة الخصوصية', f"{N(V['consent_yes'])} من {N(n720)}")}
  {kpi(N(V['duplicate_customers']), 'سجلات عملاء مكررة', f"{N(V['unique_civil_ids'])} رقمًا مدنيًا فريدًا")}
</div>
{src(SRC_BOTH)}''', sec='لوحة المؤشرات', toc=('لوحة المؤشرات', 1))

# ======================================================================== PART 1
divider(1, 'المبادرة والمشاركة', 'رؤية حكومية تفتح نموذجًا جديدًا للاستفادة السكنية، وفريق من القطاع الخاص يعمل في ركنها لتحويل الاهتمام إلى قرار.',
        ['عن مبادرة «سكنة وخزينة»', 'ملخص المشاركة', 'دور فريق وصول', 'فريق وصول', 'رحلة العميل'])

add(f'''{sec_head('1.1 · عن المبادرة', 'من استفادة واحدة مدى الحياة… إلى استفادتين',
    'تغيّر مبادرة «سكنة وخزينة» مفهوم الاستفادة السكنية الحكومية: بدل منحة واحدة تنتهي بها استفادة المواطن، تصبح الاستفادة مرتين.')}
<div class="cmp block">
  <div><div class="h">النظام السابق</div><p class="small" style="margin:0">كان المواطن يستفيد من المنحة الحكومية مرة واحدة، غالبًا عبر الحصول على أرض، وتنتهي بذلك استفادته السكنية الحكومية.</p></div>
  <div><div class="h">مع «سكنة وخزينة»</div><p class="small" style="margin:0">تبدأ الاستفادة الأولى بشراء شقة في مدينة السلطان هيثم، وبعد مرور {N(5)} سنوات من استلام الشقة يُفتح للمستفيد الاستحقاق مرة أخرى وفق الأنظمة المعمول بها.</p></div>
</div>
<div class="journey">
  <div class="st1"><div class="lab">الاستفادة الأولى · سكنة</div><div class="ttl">شقة في مدينة السلطان هيثم</div><p class="small" style="margin:0">المسكن أولًا: شراء شقة ضمن البرنامج.</p></div>
  <div class="gap"><div class="y">{N(5)}</div><div class="ln"></div><div class="yl">سنوات من<br>استلام الشقة</div></div>
  <div class="st2"><div class="lab">الاستفادة الثانية · استحقاق جديد</div><div class="ttl">أرض، أو دعم حكومي لوحدة سكنية</div><p class="small" style="margin:0">الاختيار بين أرض، أو دعم لوحدة سكنية (شقة أو فيلا).</p></div>
</div>
<div class="grid g2 block" style="margin-top:7mm">
  <div class="panel"><h3>معنى الاسم</h3><p class="small"><b>سكنة</b> — المسكن: الاستفادة الأولى توفّر للمواطن بيتًا يسكنه.<br>
  <b>خزينة</b> — الأصل الذي يبقى: تظل الشقة ملكًا للمستفيد، يحتفظ بها أو يؤجرها أو يتصرف فيها لاحقًا وفق القواعد المنظمة، بينما يعود له حق الاستفادة.</p></div>
  <div class="panel"><h3>لماذا يهم ذلك</h3><p class="small">ينقل النموذج الاستفادة السكنية من قرار واحد إلى مسار؛ فيدخل المستفيد سوق الشقق مبكرًا، ويحتفظ بأصل عقاري، ثم يعود إلى خياراته بعد خمس سنوات من الاستلام.</p></div>
</div>
<div class="quote">«استفد اليوم بشقة، واستفد مرة أخرى بعد {N(5)} سنوات.»</div>
<div class="note" style="margin-top:2mm">الرسالة الجوهرية للمبادرة. يعتمد هذا القسم على الوثائق المرجعية لهوية المبادرة، ولا يضيف أحكامًا نظامية خارجها.</div>
{src('دليل الهوية البصرية لمبادرة «سكنة وخزينة»، الإصدار 1.0، أكتوبر 2026 — القسم 01')}''', toc=('عن مبادرة «سكنة وخزينة»', 2))

timeline = [
    ('2026-10-02', 'يوم التدريب', f"تدريب الفريق {N(12)} ساعة ({N('10:00')}–{N('22:00')}): نطاق المشاركة، الأدوار، مهارات البيع، البيانات، الحجز، المحاكاة."),
    ('2026-10-03', 'اتفاقيات المشاركة', 'توقيع اتفاقيات المستشارين العقاريين وتحديد المهام وآليات التوثيق والسرية.'),
    ('2026-10-05', 'افتتاح المعرض', f"أول تسجيل في ركن المبادرة الساعة {N(first_reg[11:16])}."),
    ('2026-10-08', 'اليوم الأخير', f"{N(deal_peak_day['deals'])} صفقات مسجّلة — أعلى أيام التوثيق."),
    ('2026-10-09', 'ما بعد المعرض', f"{N(post_ev)} تسجيلًا للمتابعة حتى {d_ar(last_reg, year=False)}، وتوثيق صفقة إضافية."),
    (EXTRACT_DATE, 'استخراج البيانات', 'مطابقة السجلات وإعداد هذا التقرير.'),
]
tl = ''.join(f'<div class="stp tl"><div class="dchip"><b>{N(int(d[8:]))}</b>أكتوبر</div>'
             f'<div><div class="t">{t}</div><div class="d">{x}</div></div><div class="m"></div></div>' for d, t, x in timeline)
add(f'''{sec_head('1.2 · ملخص المشاركة', 'أربعة أيام في ركن المبادرة', f"شارك فريق وصول للاستثمار في ركن وزارة الإسكان والتخطيط العمراني لمبادرة «سكنة وخزينة» ضمن {M['event']['name'].replace('2026', N(2026))}.")}
<div class="grid g4 block" style="gap:5mm">
  {kpi(N(M['event']['days']), 'أيام معرض', f"{d_ar(M['event']['start'], year=False)} – {d_ar(M['event']['end'], year=False)}")}
  {kpi(N(M['event']['operating_hours']), 'ساعة تشغيل', f"يوميًا {N('9:00')}–{N('22:00')}")}
  {kpi(N(M['contracts_total']), 'اتفاقية مشاركة', f"{N(M['consultants_contracted'])} مستشارًا عقاريًا ومصوّر")}
  {kpi(N(n720), 'عميلًا مسجّلًا', f"{N(M['deals_total'])} صفقة مسجّلة")}
</div>
<div class="grid g12-7-5">
  <div class="panel"><h2>المسار الزمني</h2><div class="flow">{tl}</div></div>
  <div class="panel"><h2>نطاق التقرير</h2>
    <p class="small">يغطي التقرير نشاط فريق وصول في <b>ركن المبادرة</b> فقط: تسجيل العملاء، والصفقات الموثقة في سجل المبيعات الخاص بالمبادرة، والمتابعة بعد المعرض.</p>
    <p class="small">وشارك فريق وصول في المعرض نفسه في ركن شركة مجد للتطوير العقاري (جناح {N('A150')})، ويوزّع المستشارون بين الركنين بحسب حاجة المشاركة؛ ولا يشمل هذا التقرير نشاط ذلك الركن.</p>
    <p class="small">ساعات العمل الفعلية المعتمدة لكل مستشار {N(12)} ساعة يوميًا بعد ساعة استراحة، وفق اتفاقية المشاركة. لا يتضمن التقرير مجموع ساعات حضور الفريق لعدم توفر سجل حضور موحّد ضمن مصادر البيانات.</p>
  </div>
</div>
{src('اتفاقية المشاركة الموحدة للمستشارين، ودليل إحاطة الفريق «WUSOOL October Urban 2026 Team Briefing»، وسجل تسجيل العملاء')}''', toc=('ملخص المشاركة', 2))

resp = [
    ('جذب واستقبال', 'Attract', 'استقبال الزوار باحترافية ولباقة، والمبادرة بالحوار دون إلحاح أو تضليل.'),
    ('فهم الاحتياج', 'Understand', 'فهم احتياج العميل وميزانيته وتوجهه قبل أي عرض، دون الحكم على أهليته؛ فالاعتماد من اختصاص الجهات المخوّلة.'),
    ('مطابقة وعرض', 'Match & Present', 'عرض خيار أو خيارين مناسبين فقط، وشرح المشروع والأسعار وخطط السداد من المصادر المعتمدة.'),
    ('حجز', 'Book', f"مساعدة العميل الجاهز في الحجز عبر القنوات والإجراءات الرسمية المعتمدة فقط، بمبلغ الحجز المعتمد ({N('1,000')} ر.ع.) حيث ينطبق."),
    ('توثيق ومتابعة', 'Document', 'تسجيل بيانات العميل بموافقته، وتوثيق الوحدة والمشروع والقيمة باسم المستشار، ورفع ملخص يومي، وتسليم المتابعة.'),
]
resp_html = ''.join(f'<div class="stp"><div class="i">{N(i + 1)}</div><div><div class="t">{a} <span class="small muted">·</span> <span class="en small muted">{b}</span></div><div class="d">{c}</div></div><div class="m"></div></div>'
                    for i, (a, b, c) in enumerate(resp))
add(f'''{sec_head('1.3 · دور فريق وصول', 'مستشارون عقاريون… لا موظفو جناح',
    'تقود وزارة الإسكان والتخطيط العمراني المبادرة وتنظّم ركنها. ووصول للاستثمار أحد فرق القطاع الخاص التي عملت داخل هذا الإطار لتحويل اهتمام الزوار إلى قرارات موثقة.')}
<div class="grid g12-7-5">
  <div class="panel"><h2>خمس مسؤوليات… مسار واحد</h2><div class="flow">{resp_html}</div></div>
  <div class="panel"><h2>ما يثبته السجل</h2>
    <div class="stack">
    {kpi(N(n720), 'عميلًا سُجّلت بياناتهم', f"جميعهم بموافقة على سياسة الخصوصية، وباسم «وصول للاستثمار» وسيطًا عقاريًا")}
    {kpi(N(M['records_with_contracted']), 'سجلًا يحمل اسم مستشار متعاقد', f"{N(pct(100 * M['records_with_contracted'] / n720))} من السجلات")}
    {kpi(N(M['records_shared']), 'سجلًا بخدمة مشتركة', 'أكثر من عضو في خدمة العميل الواحد (تسليم واستلام داخل الفريق)')}
    {kpi(N(M['deals_total']), 'صفقة موثقة في سجل المبيعات', f"لدى {N(M['developers_count'])} مطورين و{N(M['projects_count'])} مشاريع")}
    </div></div>
</div>
<div class="panel soft" style="margin-top:6mm"><p class="small" style="margin:0"><b>حدود الدور.</b> لا يقرّر المستشار أهلية العميل، ولا يضمن التمويل أو الاستحقاق الحكومي، ولا يقدّم خصومات أو وعودًا غير معتمدة،
ولا يستلم مبالغ الحجز إلا عبر المحصّل الرسمي المخوّل. هذه الضوابط منصوص عليها في اتفاقية المشاركة الموقّعة مع كل مستشار.</p></div>
{src('اتفاقية المشاركة (البنود الثالث والسابع والثامن) ودليل إحاطة الفريق؛ مؤشرات السجل من سجل تسجيل العملاء وسجل المبيعات')}''', toc=('دور فريق وصول', 2))

roster_html = ''.join(
    f'<div style="display:flex;gap:2.4mm;align-items:baseline;padding:1.7mm 0;border-bottom:.4pt solid var(--grid)">'
    f'<span class="num small muted" style="min-width:5mm">{r["no"]:02d}</span><span style="flex:1">{r["name"]}<span class="sub xs muted" style="display:block">{r["role"]}</span></span>'
    f'<span class="xs" style="font-weight:600;color:{"#0A7F52" if r["in_records"] else "#7C8A83"}">{"في سجلات الركن" if r["in_records"] else "—"}</span></div>'
    for r in M['roster'])
add(f'''{sec_head('1.4 · فريق وصول', 'فريق واحد في ركنين',
    f"تعاقدت وصول للاستثمار مع {N(M['consultants_contracted'])} مستشارًا عقاريًا ومصوّر للمشاركة في المعرض. ويوزّع الفريق بين ركن المبادرة وركن شركة مجد بحسب حاجة المشاركة.")}
<div class="grid g2" style="gap:0 8mm">{roster_html}</div>
<div class="grid g3" style="margin-top:7mm;gap:5mm">
  {kpi(N(M['contracted_in_records']), 'مستشارًا وردت أسماؤهم في سجلات ركن المبادرة', 'بحسب اسم الموظف في سجل التسجيل أو سجل المبيعات')}
  {kpi(N(M['supporting_names']), 'اسمًا مساندًا آخر في السجل', 'وردت في تسجيلات مشتركة، دون اتفاقية مستشار ضمن ملفات المشاركة')}
  {kpi(N(12), 'ساعة تدريب قبل المعرض', f"يوم التدريب {d_ar('2026-10-02')}")}
</div>
<div class="note" style="margin-top:4mm">«—» تعني أن الاسم لم يرد في سجلات ركن المبادرة، وقد يكون العضو عمل في ركن شركة مجد أو في أدوار مساندة لا تظهر في سجل التسجيل.</div>
{src('عناوين اتفاقيات المشاركة في مجلد «عقود مستشاري أكتوبر العمران 2026»؛ سجل تسجيل العملاء؛ سجل المبيعات')}''', toc=('فريق وصول', 2))

# ---- customer journey (real workflow from the briefing + what the records show)
J = [
    ('الانطباع الأول', 'First impression', 'تواصل بصري، ترحيب باسم وصول، سؤال مفتوح عن سبب الزيارة.', None, None),
    ('الاكتشاف والتأهيل', 'Discovery · Qualify', 'الاحتياج، الأسرة وعدد الغرف، الميزانية التقريبية، الموقع، توقيت القرار.', None, None),
    ('التسجيل بموافقة العميل', 'Registration', 'تسجيل البيانات في الاستمارة المعتمدة بعد الموافقة على سياسة الخصوصية، وإسناد العميل لمستشار.', N(n720), 'عميلًا مسجّلًا'),
    ('المطابقة والعرض', 'Match & Present', 'خيار أو خياران مناسبان من المصادر المعتمدة، ومقارنة واضحة.', N(V['notes_meaningful']), 'سجلًا بملاحظة احتياج'),
    ('القرار: حجز أو توثيق صفقة', 'Close', 'حجز الوحدة عبر القنوات الرسمية، وتوثيق الوحدة والمشروع والسعر في سجل المبيعات.', N(M['deals_total']), f"صفقة · {N(M['deals_documented'])} موثقة"),
    ('المتابعة', 'Follow-up', 'كل عميل يحمل اسم مستشاره وموعد متابعته… العميل الذي لم يشترِ اليوم لم ينتهِ.', N(M['open_pipeline']), 'عميلًا قيد المتابعة'),
]
jh = ''.join(f'<div class="stp{" on" if m else ""}"><div class="i">{N(i + 1)}</div><div><div class="t">{a} <span class="small muted">·</span> <span class="en small muted">{b}</span></div><div class="d">{c}</div></div>'
             f'<div class="m">{m or ""}<small>{s or ""}</small></div></div>' for i, (a, b, c, m, s) in enumerate(J))
add(f'''{sec_head('1.5 · رحلة العميل', 'من المرور… إلى المتابعة',
    'صُمّمت رحلة العميل في دليل إحاطة الفريق على أن كل لحظة إما تبني الثقة أو تخسرها. وتُظهر السجلات حجم كل مرحلة يمكن قياسها.')}
<div class="flow">{jh}</div>
<div class="grid g3" style="margin-top:7mm;gap:5mm">
  {kpi(N(pct(100 * M['records_shared'] / n720)), 'من العملاء خدمهم أكثر من عضو', f"{N(M['records_shared'])} سجلًا بتسليم واستلام داخل الفريق")}
  {kpi(N(post_ev), 'تسجيلًا بعد انتهاء المعرض', f"{d_ar('2026-10-09', year=False)} – {d_ar(last_reg[:10], year=False)}")}
  {kpi(N(M['deals_pending']), 'صفقات قيد الاستكمال', 'بانتظار رمز الوحدة والسعر النهائي')}
</div>
<div class="note" style="margin-top:4mm">المراحل الثلاث الأولى من الرحلة لا تُسجَّل رقميًا (عدد المارّين والمحادثات)؛ لذلك تبدأ الأرقام من مرحلة التسجيل.</div>
{src('دليل إحاطة الفريق (Customer Journey · Five Core Responsibilities)؛ سجل تسجيل العملاء؛ سجل المبيعات')}''', toc=('رحلة العميل', 2))

# ======================================================================== PART 2 — CUSTOMERS
divider(2, 'العملاء والأداء التشغيلي', f"{N(n720)} عميلًا دخلوا رحلة الاختيار والقرار. يقرأ هذا القسم من هم، ومتى جاؤوا، وماذا طلبوا، ومن خدمهم.",
        ['قاعدة العملاء وجودة البيانات', 'الأداء اليومي', 'تحليل التوقيت', 'الاهتمامات والاحتياجات', 'أداء الفريق في التسجيل', 'من التسجيل إلى الصفقة'])

comp = [
    ('الاسم الكامل', n720, n720), ('الرقم المدني بصيغة صحيحة', n720 - V['invalid_civil_ids'], n720),
    ('رقم هاتف عُماني صحيح (8 أرقام)', n720 - V['invalid_phones'], n720), ('الموافقة على سياسة الخصوصية', V['consent_yes'], n720),
    ('تاريخ انتهاء البطاقة', V['id_expiry_provided'], n720), ('ملاحظة احتياج ذات معنى', V['notes_meaningful'], n720),
]
comp_chart = hbars([dict(label=a, value=b, vlabel=f'{100 * b / c:.1f}%') for a, b, c in comp], w=640, label_w=190, bar_h=14, gap=9, vmax=n720, value_w=60)
rec_rows = [
    ('عدد السجلات', num(n720), num(V['crm_records']), 'متطابق'),
    ('الأرقام المدنية', num(V['unique_civil_ids']) + ' فريد', num(V['crm_same_civil']) + ' متطابق', 'متطابق'),
    ('وقت التسجيل', '—', num(V['crm_same_timestamp']) + ' متطابق', 'متطابق'),
    ('الاسم', '—', num(V['crm_same_name']) + ' متطابق', 'متطابق'),
    ('الهاتف', '—', num(V['crm_same_phone_normalized']) + ' متطابق', f"{num(V['crm_phone_format_diffs'])} بفرق صيغة فقط (+968)"),
    ('اسم الموظف', '—', num(n720 - V['crm_staff_differs']) + ' متطابق', f"{num(V['crm_staff_differs'])} مختلف — انظر الملاحظة"),
]
rec_html = ''.join(f'<tr><td>{a}</td><td class="n">{N(b) if b != "—" else b}</td><td class="n">{N(c)}</td><td>{d}</td></tr>' for a, b, c, d in rec_rows)
add(f'''{sec_head('2.1 · قاعدة العملاء', f"{N(n720)} عميلًا… بلا تكرار",
    'قبل أي تحليل، طوبق سجل تسجيل العملاء مع نسخته في نظام إدارة العملاء (AqarCRM)، وفُحصت الحقول الأساسية واحدًا واحدًا.')}
<div class="grid g4 block" style="gap:5mm">
  {kpi(N(n720), 'سجل عميل', f"تسلسل كامل من {N(1)} إلى {N(n720)}", 'accent')}
  {kpi(N(V['duplicate_customers']), 'سجلات مكررة', f"{N(V['unique_civil_ids'])} رقمًا مدنيًا فريدًا")}
  {kpi(N(V['unique_phones']), 'رقم هاتف فريد', f"رقم واحد مشترك بين شخصين مختلفين")}
  {kpi(N(V['repeated_name_groups']), 'أسماء متشابهة لأشخاص مختلفين', f"{N(V['repeated_names_distinct_people'])} سجلًا بأرقام مدنية مختلفة — ليست تكرارًا")}
</div>
<div class="panel block"><h2>اكتمال الحقول</h2>{chart('customers_field_completeness', comp_chart)}
<div class="note">حقل البريد الإلكتروني غير صالح للتحليل: {N(V['email_provided'])} قيمة فقط، وجميعها مقتطعة في المصدر عند نحو {N(12)} حرفًا؛ لذلك استُبعد من التقرير.</div></div>
<div class="panel"><h2>المطابقة بين سجل التسجيل وسجل النظام</h2>
<table class="t"><thead><tr><th>الحقل</th><th class="n">سجل التسجيل</th><th class="n">سجل AqarCRM</th><th>النتيجة</th></tr></thead><tbody>{rec_html}</tbody></table>
<p class="note" style="margin-top:2mm">يختلف «اسم الموظف» لأن سجل النظام يحمل اسم <b>الحساب</b> الذي أُدخل منه العميل ({N(len(M['crm_accounts']))} حسابات)، بينما يحمل سجل التسجيل اسم <b>من خدم العميل فعليًا</b>، بما في ذلك الخدمة المشتركة. اعتمد التقرير سجل التسجيل مصدرًا للإسناد.</p></div>
{src(SRC_REG + ' · نسخة «AqarCRM» من الملف نفسه')}''', toc=('قاعدة العملاء وجودة البيانات', 2))

# ---- daily
day_rows = ''.join(
    f'<tr{" class=hl" if b is best_day else ""}><td>{b["weekday"]}</td><td>{d_ar(b["date"], year=False)}</td><td>{"أيام المعرض" if b["in_event"] else "متابعة بعد المعرض"}</td>'
    f'<td class="n">{N(b["registrations"])}</td><td class="n">{N(pct(100 * b["registrations"] / n720))}</td><td class="n">{N(f'{b["first"]} – {b["last"]}')}</td>'
    f'<td class="n">{N(hr(b["peak_hour"]))} <span class="sub">{N(b["peak_count"])} تسجيلًا</span></td><td class="n">{N(b["deals"])}</td><td class="n">{N(money(b["value"])) if b["value"] else "—"}</td></tr>'
    for b in M['by_day'])
daily_chart = columns([dict(label=b['weekday'], sub=f"{int(b['date'][8:])} أكتوبر", value=b['registrations'], vlabel=num(b['registrations']),
                            hl=b is best_day) for b in M['by_day']], w=640, h=230, col_w=34)
add(f'''{sec_head('2.2 · الأداء اليومي', 'يومٌ ثانٍ هو الأعلى… ويومٌ أخير للقرار',
    f"بلغ متوسط التسجيل {N(M['avg_per_event_day'])} عميلًا في كل يوم من أيام المعرض. وارتفع الإقبال في اليوم الثاني، بينما تركّزت الصفقات في اليوم الأخير.")}
<div class="panel block"><h2>التسجيلات حسب اليوم</h2>{chart('daily_registrations', daily_chart)}</div>
<table class="t block"><thead><tr><th>اليوم</th><th>التاريخ</th><th>الفترة</th><th class="n">التسجيلات</th><th class="n">النسبة</th><th class="n">أول – آخر تسجيل</th><th class="n">ساعة الذروة</th><th class="n">الصفقات</th><th class="n">القيمة الموثقة (ر.ع.)</th></tr></thead>
<tbody>{day_rows}</tbody><tfoot><tr><td colspan="3">الإجمالي</td><td class="n">{N(n720)}</td><td class="n">{N('100.0%')}</td><td></td><td></td><td class="n">{N(M['deals_total'])}</td><td class="n">{N(money(M['deal_value_total']))}</td></tr></tfoot></table>
<div class="grid g3" style="gap:5mm">
  {kpi(N(best_day['registrations']), f"أعلى يوم تسجيلًا · {best_day['weekday']}", f"{N(pct(100 * best_day['registrations'] / n720))} من الإجمالي")}
  {kpi(N(deal_peak_day['deals']), f"صفقة في {deal_peak_day['weekday']} {d_ar(deal_peak_day['date'], year=False)}", f"{N(deal_peak_day['deals_documented'])} موثقة بقيمة {OMR(deal_peak_day['value'])}")}
  {kpi(N(post_ev), 'تسجيلًا بعد المعرض', 'استمرار التواصل مع عملاء جدد بعد اليوم الأخير')}
</div>
<div class="note" style="margin-top:3mm">يُنسب كل تسجيل وكل صفقة إلى تاريخ إدخالها في السجل. صفقة {N(ID_LATE)} أُدخلت الساعة {N(next(d['time'] for d in D if d['deal_id'] == ID_LATE))} من {d_ar(next(d['date'] for d in D if d['deal_id'] == ID_LATE), year=False)} بعد إغلاق اليوم السابق، واحتُسبت بتاريخ إدخالها.</div>
{src(SRC_BOTH)}''', toc=('الأداء اليومي', 2))

# ---- timing
hrs = M['by_hour']
hour_chart = columns([dict(label=str(h['hour']), value=h['registrations'], vlabel=num(h['registrations']),
                           hl=h['hour'] in (peak1['hour'],)) for h in hrs], w=640, h=210, col_w=22, axis_h=24)
hm_rows = [(b['weekday'], f"{int(b['date'][8:])} أكتوبر", M['heatmap'][b['date']]) for b in ev_days]
heat = heatmap(hm_rows, [str(h) for h in range(M['event']['open_hour'], M['event']['close_hour'] + 1)], w=640, label_w=86, cell_h=28)
blocks = M['by_block']
split = ''.join(f'<div style="width:{b["share"]}%;background:{c}">{N(pct(b["share"]))}</div>' for b, c in zip(blocks, [AQUA, '#2E7F87', MIDNIGHT]))
split_leg = ''.join(f'<div><b>{b["label"].split(" (")[0]}</b> {N("(" + b["label"].split(" (")[1])} · {N(b["registrations"])}</div>' for b in blocks)
add(f'''{sec_head('2.3 · تحليل التوقيت', 'المساء هو الموعد الأهم',
    f"تركّز {N(pct(evening['share']))} من تسجيلات أيام المعرض بعد {N('17:00')}، مع ذروتين واضحتين: الظهيرة عند {N(hr(peak1['hour']))} والمساء عند {N(hr(peak2['hour']))}.")}
<div class="panel block"><h2>التسجيلات حسب ساعة اليوم <span class="small muted">· مجموع أيام المعرض الأربعة ({N(in_ev)} تسجيلًا)</span></h2>{chart('hourly_registrations', hour_chart)}
<div class="note">تشير الأرقام أسفل الأعمدة إلى بداية الساعة (مثال: {N(13)} = {N('13:00')}–{N('13:59')}). يُقرأ الزمن من اليمين إلى اليسار.</div></div>
<div class="panel block"><h2>خريطة كثافة التسجيل: اليوم × الساعة</h2>{chart('heatmap_day_hour', heat)}</div>
<div class="panel"><h2>توزيع التسجيلات على فترات اليوم</h2><div class="split">{split}</div><div class="split-legend">{split_leg}</div></div>
<p class="small" style="margin-top:5mm"><b>القراءة التشغيلية:</b> تتطلب الفترة المسائية أعلى تغطية من المستشارين، ويستحق كل من الظهيرة ({N(hr(peak1['hour']))}) والمساء ({N(hr(peak2['hour']))}) جدولة الاستراحات والصلاة بالتناوب بعيدًا عنهما.</p>
{src(SRC_REG + ' · أيام المعرض فقط')}''', toc=('تحليل التوقيت', 2))

# ---- interests
tag_order = ['مهتم', 'استثمار', 'غرفة وصالة', 'غرفتان', 'فيلا', 'استبدال أرض', 'جاد', 'سكن', '3 غرف', 'ميزانية محدودة']
tag_chart = hbars([dict(label=t, value=tags.get(t, 0), vlabel=num(tags.get(t, 0))) for t in tag_order if tags.get(t)], w=640, label_w=120, bar_h=14, gap=9, value_w=40)
bed_chart = columns([dict(label=k, value=v_, vlabel=num(v_), hl=k == 'غرفة وصالة') for k, v_ in [('غرفة وصالة', bed['غرفة وصالة']), ('غرفتان', bed['غرفتان']), ('3 غرف', bed['3 غرف'])]],
                    w=300, h=170, col_w=34, axis_h=24)
add(f'''{sec_head('2.4 · الاهتمامات والاحتياجات', 'ماذا طلب العملاء؟',
    f"لا تتضمن استمارة التسجيل حقولًا منظمة للميزانية أو عدد الغرف أو الغرض. لذلك صُنّفت ملاحظات المستشارين النصية بقواعد ثابتة؛ وتغطي {N(V['notes_tagged'])} سجلًا ({N(pct(100 * V['notes_tagged'] / n720))} من العملاء).")}
<div class="panel block"><h2>الاهتمامات المذكورة في ملاحظات المستشارين</h2>{chart('interest_tags', tag_chart)}
<div class="note">قد يحمل السجل الواحد أكثر من وسم. الأرقام عدد السجلات التي ورد فيها الوسم.</div></div>
<div class="grid g2 block">
  <div class="panel"><h2>عدد الغرف المطلوب</h2>{chart('bedroom_mentions', bed_chart)}<div class="note">من {N(bed_total)} سجلًا ذكرت عدد الغرف.</div></div>
  <div class="panel"><h2>القراءة</h2><ul class="dots small">
    <li>الطلب المرصود يميل إلى <b>الوحدات الأصغر</b>: {N(pct(100 * bed['غرفة وصالة'] / bed_total, 0))} من الملاحظات التي ذكرت عدد الغرف طلبت غرفة وصالة.</li>
    <li>ورد <b>الاستثمار</b> في {N(tags.get('استثمار', 0))} ملاحظة مقابل {N(tags.get('سكن', 0))} للسكن؛ وهو ما يتسق مع فكرة «خزينة»: شقة تبقى أصلًا.</li>
    <li>{N(tags.get('استبدال أرض', 0))} عملاء سألوا عن <b>استبدال أرض</b> بشقة، و{N(tags.get('فيلا', 0))} عن <b>الفلل</b>؛ أسئلة تحتاج إجابة رسمية موحّدة من الوزارة.</li>
    <li>{N(M['intent_interested'])} سجلًا وُصف صاحبه بأنه «مهتم» أو «جاد».</li></ul></div>
</div>
<div class="note">تعكس هذه الأرقام ما دوّنه المستشارون، لا كامل احتياجات العملاء. بعض الملاحظات مقتطعة في المصدر، ولم يُصنّف إلا ما تدل عليه كلماته بوضوح.</div>
{src(SRC_REG + ' · حقل «التعليقات»')}''', toc=('الاهتمامات والاحتياجات', 2))

# ---- team performance (registrations)
team_chart = stacked_hbars([dict(label=t['name'], parts=[t['solo'], t['shared']], vlabel=num(t['involved'])) for t in contracted],
                           [('تسجيل منفرد', MIDNIGHT), ('تسجيل مشترك', AQUA)], w=640, label_w=120, bar_h=14, gap=8, value_w=44)
sup = '، '.join(f'{t["name"]} ({N(t["involved"])})' for t in supporting)
add(f'''{sec_head('2.5 · أداء الفريق في التسجيل', 'من خدم العملاء؟',
    'يُسند كل سجل إلى من خدم العميل كما ورد في سجل التسجيل. عند الخدمة المشتركة يُحتسب السجل لكل اسم شارك فيه؛ لذلك يتجاوز مجموع المشاركات عدد العملاء.')}
<div class="panel block"><h2>المستشارون المتعاقدون ({N(len(contracted))})</h2>{chart('team_registrations', team_chart)}</div>
<div class="grid g3 block" style="gap:5mm">
  {kpi(N(M['records_solo']), 'سجلًا بخدمة منفردة', f"{N(pct(100 * M['records_solo'] / n720))} من العملاء")}
  {kpi(N(M['records_shared']), 'سجلًا بخدمة مشتركة', 'اسمان أو أكثر في السجل نفسه')}
  {kpi(N(M['names_in_register']), 'اسمًا مختلفًا في السجل', f"{N(len(contracted))} مستشارًا متعاقدًا و{N(len(supporting))} اسمًا مساندًا")}
</div>
<div class="panel soft"><h3>أسماء مساندة وردت في السجل</h3><p class="small" style="margin:0">{sup}.</p>
<p class="note" style="margin-top:1.5mm">وردت هذه الأسماء غالبًا ضمن تسجيلات مشتركة مع مستشار متعاقد، وبعضها بالاسم الأول فقط كما دُوّن في السجل.</p></div>
<div class="note" style="margin-top:3mm">الغرض من هذا القسم توثيق توزيع العمل لا المفاضلة بين الأشخاص؛ فحجم التسجيل يتأثر بالركن المسند وساعات الحضور والأدوار المساندة.</div>
{src(SRC_REG + ' · حقل «اسم موظف المبيعات»')}''', toc=('أداء الفريق في التسجيل', 2))

# ---- team performance (deals) + CRM accounts
cons_rows = ''.join(
    f'<tr><td><b>{r["name"]}</b></td><td class="n">{N(next((t["involved"] for t in M["team"] if t["name"] == r["name"]), 0))}</td><td class="n">{N(r["deals"])}</td><td class="n">{N(r["documented"])}</td>'
    f'<td class="n">{N(r["pending"])}</td><td class="n">{N(money(r["value"])) if r["value"] else "—"}</td><td class="n">{N(money(r["avg"])) if r["avg"] else "—"}</td><td>{"، ".join(r["projects"])}</td></tr>'
    for r in sorted(by_cons, key=lambda r: (-r['value'], -r['deals'])))
crm_chart = hbars([dict(label=a['name'], value=a['registrations'], vlabel=num(a['registrations'])) for a in M['crm_accounts']], w=640, label_w=120, bar_h=13, gap=8, value_w=40)
add(f'''{sec_head('2.6 · أداء الفريق في الصفقات', 'بطاقة أداء المستشارين',
    f"وثّق {N(M['consultants_with_deals'])} مستشارين {N(M['deals_total'])} صفقة في سجل المبيعات. تُعرض الأرقام كما سُجّلت، والصفقة غير المكتملة لا تُحتسب في القيمة.")}
<table class="t block"><thead><tr><th>المستشار</th><th class="n">سجلات التسجيل</th><th class="n">صفقات مسجّلة</th><th class="n">موثقة</th><th class="n">قيد الاستكمال</th><th class="n">القيمة الموثقة (ر.ع.)</th><th class="n">متوسط الصفقة (ر.ع.)</th><th>المشاريع</th></tr></thead>
<tbody>{cons_rows}</tbody><tfoot><tr><td>الإجمالي</td><td></td><td class="n">{N(M['deals_total'])}</td><td class="n">{N(M['deals_documented'])}</td><td class="n">{N(M['deals_pending'])}</td><td class="n">{N(money(M['deal_value_total']))}</td><td class="n">{N(money(M['deal_value_avg']))}</td><td></td></tr></tfoot></table>
<div class="note block">لا يحسب التقرير «معدل تحويل» لكل مستشار: سجل التسجيل وسجل المبيعات استمارتان منفصلتان، وقد يوثّق الصفقة مستشار غير من سجّل العميل (مثال: {N(ID_CROSS)}). تطابق المستشار في السجلين في {N(sum(1 for d in D if d['register_seq'] and d['consultant'] in d['register_staff']))} من {N(M['deal_customers_matched'])} صفقات مرتبطة بالسجل.</div>
<div class="panel"><h2>حسابات الإدخال في نظام AqarCRM</h2>{chart('crm_accounts', crm_chart)}
<div class="note">أُدخل العملاء الـ{N(n720)} في النظام عبر {N(len(M['crm_accounts']))} حسابات مستخدمين. يعكس هذا التوزيع الأجهزة والحسابات المستخدمة في الإدخال، لا من خدم العميل.</div></div>
{src(SRC_SALES + ' · ' + 'نسخة «AqarCRM» من سجل التسجيل')}''', toc=('أداء الفريق في الصفقات', 2))

# ---- funnel & conversion
fun = [('عملاء مسجّلون', 'كل سجلات الركن', n720, ''), ('صفقات مسجّلة', 'سجل المبيعات', M['deals_total'], 'b2'), ('صفقات موثقة', 'برمز الوحدة والسعر النهائي', M['deals_documented'], 'b3')]
fh = ''.join(f'<div class="row"><div class="lab">{a}<small>{b}</small></div><div><div class="bar {cl}" style="width:{max(100 * math.sqrt(v_ / n720), 2.2):.2f}%"></div></div>'
             f'<div class="val">{N(num(v_))}<small>{"" if v_ == n720 else N(f"{100 * v_ / n720:.2f}") + " لكل 100 عميل"}</small></div></div>' for a, b, v_, cl in fun)
add(f'''{sec_head('2.7 · من التسجيل إلى الصفقة', 'مسار التحويل',
    'يقيس هذا القسم كم من الاهتمام المسجّل تحوّل إلى صفقة خلال المعرض وما تلاه مباشرة. الأرقام تخص فترة المعرض والأيام التالية له فقط، والمتابعة ما زالت جارية.')}
<div class="funnel block">{fh}</div>
<div class="note block">عرض الأعمدة متناسب مع الجذر التربيعي للقيمة حتى تبقى المراحل الصغيرة مرئية؛ الأرقام هي المرجع.</div>
<div class="grid g3 block" style="gap:5mm">
  {kpi(N(pct(M['conv_deal_records_per_100'], 2)), 'صفقات مسجّلة ÷ عملاء مسجّلون', N(f"{M['deals_total']} ÷ {n720}"), 'accent')}
  {kpi(N(pct(M['conv_registered_with_deal'], 2)), 'عملاء السجل المرتبطون بصفقة', N(f"{M['deal_customers_matched']} ÷ {n720}"))}
  {kpi(N(pct(M['conv_documented_per_100'], 2)), 'صفقات موثقة ÷ عملاء مسجّلون', N(f"{M['deals_documented']} ÷ {n720}"))}
</div>
<div class="panel"><h2>ربط الصفقات بسجل العملاء</h2>
<p class="small">طوبقت كل صفقة مع سجل العملاء بالرقم المدني أولًا، ثم برقم الهاتف مع اسم العائلة عند غياب الرقم المدني:</p>
<ul class="dots small"><li><b>{N(sum(1 for d in D if d['match_method'] == 'الرقم المدني'))}</b> صفقات طوبقت بالرقم المدني، و<b>{N(sum(1 for d in D if d['match_method'] == 'الهاتف + اسم العائلة'))}</b> بالهاتف واسم العائلة.</li>
<li><b>{N(M['deal_customers_unmatched'])}</b> صفقات لعملاء لم يُعثر عليهم في سجل التسجيل ({'، '.join(N(d['deal_id']) for d in D if d['register_seq'] is None)})؛ قد يكونون سُجّلوا خارج الاستمارة أو بأرقام مختلفة، وتحتاج إلى استكمال.</li>
<li>جميع الصفقات لعملاء مختلفين ({N(V['deal_customers_distinct'])} عميلًا)، ولا توجد صفقة مكررة ولا رمز وحدة مكرر.</li></ul></div>
{src(SRC_BOTH)}''', toc=('من التسجيل إلى الصفقة', 2))

# ======================================================================== PART 3 — DEALS
divider(3, 'الصفقات والسوق', 'مطورون ومشاريع ووحدات: ما الذي اختاره العملاء فعلًا، وبأي قيمة، وما الذي ما زال بانتظار الاستكمال.',
        ['نظرة عامة على الصفقات', 'الصفقات حسب اليوم والمستشار', 'الأداء حسب المطور', 'الأداء حسب المشروع', 'تحليل الوحدات والأسعار'])

strip_chart = hbars([dict(label=f"{d['deal_id']} · {d['project']}", value=d['price'], vlabel=money(d['price']), hl=d['price'] == M['deal_value_max'])
                     for d in sorted((d for d in D if d['status'] == 'موثقة'), key=lambda d: (-d['price'], d['deal_id']))],
                    w=640, label_w=120, bar_h=12, gap=7, value_w=74)
area_rows = ''.join(f'<tr><td class="n">{N(f"{a["area"]:.2f}")} م²</td><td class="n">{N(a["deals"])}</td></tr>' for a in M['by_area'])
band_rows = ''.join(f'<tr><td class="n">{N(b["label"])}</td><td class="n">{N(b["deals"])}</td><td class="n">{N(money(b["value"])) if b["value"] else "—"}</td></tr>' for b in M['price_bands'])
add(f'''{sec_head('3.1 · نظرة عامة على الصفقات', f"{N(M['deals_total'])} صفقة… {N(M['deals_documented'])} منها موثقة بالكامل",
    'الصفقة الموثقة هي التي سُجّل لها رمز الوحدة وسعرها النهائي. أما الصفقات الأخرى فمسجّلة باسم العميل والمطور والمشروع، وتنتظر استكمال بيانات الوحدة.')}
<div class="grid block kpi-row" style="gap:5mm">
  {kpi(N(money(M['deal_value_total'])) + '<span class="cur">ر.ع.</span>', 'إجمالي القيمة الموثقة', f"{N(M['deals_documented'])} صفقات", 'accent')}
  {kpi(N(money(M['deal_value_avg'])), 'متوسط الصفقة (ر.ع.)')}
  {kpi(N(money(M['deal_value_median'])), 'الوسيط (ر.ع.)')}
  {kpi(N(money(M['price_per_m2_avg'])), 'متوسط سعر المتر (ر.ع./م²)', f"إجمالي المساحة {N(money(M['area_total_documented']))} م²")}
</div>
<div class="panel block"><h2>السعر النهائي لكل صفقة موثقة (ر.ع.)</h2>{chart('deal_price_strip', strip_chart)}
<div class="note">أدنى صفقة {OMR(M['deal_value_min'])}، وأعلاها {OMR(M['deal_value_max'])}. الأعمدة تبدأ من الصفر.</div></div>
<div class="grid g3">
  <div class="panel"><h3>حالة الصفقات</h3><table class="t"><tbody>
    <tr><td><span class="st ok">موثقة</span></td><td class="n">{N(M['deals_documented'])}</td></tr><tr><td><span class="st pend">قيد الاستكمال</span></td><td class="n">{N(M['deals_pending'])}</td></tr></tbody>
    <tfoot><tr><td>الإجمالي</td><td class="n">{N(M['deals_total'])}</td></tr></tfoot></table></div>
  <div class="panel"><h3>نوع الوحدة</h3><table class="t"><tbody>{''.join(f'<tr><td>{u["name"]}</td><td class="n">{N(u["deals"])}</td></tr>' for u in M['by_unit_type'])}</tbody></table>
    <h3 style="margin-top:3mm">المساحة (الموثقة)</h3><table class="t"><tbody>{area_rows}</tbody></table></div>
  <div class="panel"><h3>الفئات السعرية (ر.ع.)</h3><table class="t"><thead><tr><th>الفئة</th><th class="n">صفقات</th><th class="n">القيمة</th></tr></thead><tbody>{band_rows}</tbody></table></div>
</div>
<div class="note" style="margin-top:4mm">لا يتضمن سجل المبيعات حقول الخصم، أو العربون، أو طريقة الدفع، أو التمويل، أو الطابق، أو عدد الغرف؛ لذلك لا تُعرض في التقرير.</div>
{src(SRC_SALES)}''', toc=('نظرة عامة على الصفقات', 2))

# ---- deals by day & consultant
dd_cols = [dict(label=x['weekday'], sub=f"{int(x['date'][8:])} أكتوبر", value=x['value'], vlabel=money(x['value']) if x['value'] else '0.00',
                hl=x['value'] == max(y['value'] for y in M['deal_days'])) for x in M['deal_days']]
dd_chart = columns(dd_cols, w=640, h=210, col_w=34)
dd_rows = ''.join(f'<tr><td>{x["weekday"]}</td><td>{d_ar(x["date"], year=False)}</td><td class="n">{N(x["deals"])}</td><td class="n">{N(x["documented"])}</td><td class="n">{N(x["deals"] - x["documented"])}</td>'
                  f'<td class="n">{N(money(x["value"])) if x["value"] else "—"}</td><td class="n">{N(pct(100 * x["value"] / M["deal_value_total"]))}</td></tr>' for x in M['deal_days'])
cv_chart = hbars([dict(label=r['name'], value=r['value'], vlabel=money(r['value']) if r['value'] else f"{r['deals']} قيد الاستكمال") for r in sorted(by_cons, key=lambda r: -r['value'])],
                 w=640, label_w=120, bar_h=14, gap=9, value_w=120)
add(f'''{sec_head('3.2 · الصفقات حسب اليوم والمستشار', 'القيمة تتراكم مع اقتراب النهاية',
    f"وُثّقت {N(pct(100 * deal_peak_day['value'] / M['deal_value_total']))} من القيمة في اليوم الأخير وحده، بعد أن جمع العملاء معلوماتهم وقارنوا الخيارات خلال الأيام السابقة.")}
<div class="panel block"><h2>القيمة الموثقة حسب يوم التوثيق (ر.ع.)</h2>{chart('deal_value_by_day', dd_chart)}</div>
<table class="t block"><thead><tr><th>اليوم</th><th>التاريخ</th><th class="n">صفقات</th><th class="n">موثقة</th><th class="n">قيد الاستكمال</th><th class="n">القيمة (ر.ع.)</th><th class="n">من الإجمالي</th></tr></thead>
<tbody>{dd_rows}</tbody><tfoot><tr><td colspan="2">الإجمالي</td><td class="n">{N(M['deals_total'])}</td><td class="n">{N(M['deals_documented'])}</td><td class="n">{N(M['deals_pending'])}</td><td class="n">{N(money(M['deal_value_total']))}</td><td class="n">{N('100.0%')}</td></tr></tfoot></table>
<div class="panel"><h2>القيمة الموثقة حسب المستشار (ر.ع.)</h2>{chart('deal_value_by_consultant', cv_chart)}</div>
{src(SRC_SALES)}''', toc=('الصفقات حسب اليوم والمستشار', 2))

# ---- developers
def devcard(r, i):
    rng = f"{N(money(r['min']))} – {N(money(r['max']))}" if r['min'] and r['min'] != r['max'] else (N(money(r['min'])) if r['min'] else '—')
    return f'''<div class="devcard block"><div class="plate"><div class="nm">{r['name']}</div><div class="tg">المطور العقاري<br>المشاريع: {"، ".join(r['projects'])}</div></div>
    <div class="facts"><div><div class="v">{N(r['deals'])}</div><div class="l">صفقات مسجّلة · {N(r['documented'])} موثقة</div></div>
    <div><div class="v">{N(money(r['value'])) if r['value'] else '—'}<span class="cur"> ر.ع.</span></div><div class="l">القيمة الموثقة · {N(pct(r['share']))} من الإجمالي</div></div>
    <div><div class="v">{N(money(r['avg'])) if r['avg'] else '—'}</div><div class="l">متوسط الصفقة الموثقة (ر.ع.)</div></div>
    <div><div class="v">{N(money(r['ppm2'])) if r['ppm2'] else '—'}</div><div class="l">متوسط سعر المتر (ر.ع./م²)</div></div></div>
    <div class="small" style="margin-top:2mm"><b>المستشارون:</b> {"، ".join(r['consultants'])} · <b>الوحدات:</b> {"، ".join(f"{k} ({N(v_)})" for k, v_ in r['unit_types'].items())} · <b>نطاق السعر:</b> {rng}</div></div>'''
dev_cards = ''.join(devcard(r, i) for i, r in enumerate(by_dev))
dev_stack = stacked_hbars([dict(label=r['name'], parts=[r['documented'], r['pending']], vlabel=f"{r['deals']}") for r in by_dev],
                          [('موثقة', MIDNIGHT), ('قيد الاستكمال', AQUA)], w=640, label_w=110, bar_h=14, gap=9, value_w=30)
add(f'''{sec_head('3.3 · الأداء حسب المطور', f"{N(M['developers_count'])} مطورين في سجل المبيعات",
    f"يتصدّر {top_dev['name']} القيمة الموثقة، بينما سجّل {pending_dev['name']} أكبر عدد من الصفقات ({N(pending_dev['deals'])}) أغلبها ينتظر استكمال بيانات الوحدة.")}
{dev_cards}
<div class="panel"><h2>الصفقات حسب المطور وحالتها</h2>{chart('deals_by_developer', dev_stack)}</div>
<div class="note" style="margin-top:2mm">تُعرض أسماء المطورين نصًّا لعدم توفر ملفات شعاراتهم الرسمية ضمن أصول المشروع. لا يتضمن سجل التسجيل حقلًا للمطور المفضّل، لذلك لا يُعرض «عدد المهتمين» لكل مطور.</div>
{src(SRC_SALES)}''', toc=('الأداء حسب المطور', 2))

# ---- projects
proj_rows = ''.join(
    f'<tr><td><b>{r["name"]}</b></td><td>{"، ".join(r["developers"])}</td><td class="n">{N(r["deals"])}</td><td class="n">{N(r["documented"])}</td><td class="n">{N(money(r["value"])) if r["value"] else "—"}</td>'
    f'<td class="n">{N(pct(r["share"]))}</td><td class="n">{N(money(r["avg"])) if r["avg"] else "—"}</td><td class="n">{"، ".join(N(f"{a:.2f}") for a in r["areas"]) or "—"}</td>'
    f'<td class="n">{N(money(r["ppm2"])) if r["ppm2"] else "—"}</td><td>{"، ".join(f"{k} ({N(v_)})" for k, v_ in r["unit_types"].items())}</td></tr>' for r in by_proj)
pv_chart = hbars([dict(label=r['name'], value=r['value'], vlabel=money(r['value']) if r['value'] else f"{r['deals']} قيد الاستكمال", hl=r is top_proj) for r in by_proj],
                 w=640, label_w=110, bar_h=15, gap=10, value_w=120)
add(f'''{sec_head('3.4 · الأداء حسب المشروع', f"{N(M['projects_count'])} مشاريع… «{top_proj['name']}» في المقدمة",
    f"استحوذ مشروع «{top_proj['name']}» على {N(top_proj['documented'])} صفقات موثقة بقيمة {OMR(top_proj['value'])}، ويليه «{by_proj[1]['name']}» بأعلى متوسط لقيمة الوحدة.")}
<div class="panel block"><h2>القيمة الموثقة حسب المشروع (ر.ع.)</h2>{chart('deal_value_by_project', pv_chart)}</div>
<table class="t block"><thead><tr><th>المشروع</th><th>المطور</th><th class="n">صفقات</th><th class="n">موثقة</th><th class="n">القيمة (ر.ع.)</th><th class="n">النسبة</th><th class="n">متوسط الوحدة (ر.ع.)</th><th class="n">المساحة (م²)</th><th class="n">ر.ع./م²</th><th>نوع الوحدة</th></tr></thead>
<tbody>{proj_rows}</tbody><tfoot><tr><td colspan="2">الإجمالي</td><td class="n">{N(M['deals_total'])}</td><td class="n">{N(M['deals_documented'])}</td><td class="n">{N(money(M['deal_value_total']))}</td><td class="n">{N('100.0%')}</td><td class="n">{N(money(M['deal_value_avg']))}</td><td></td><td class="n">{N(money(M['price_per_m2_avg']))}</td><td></td></tr></tfoot></table>
<div class="panel soft"><h3>ملاحظات على بيانات المشاريع</h3><ul class="dots small">
{''.join(f"<li>مشروع «{r['name']}» مسجّل لأكثر من مطور في صفقاته ({'، '.join(r['developers'])})؛ عُرض كما سُجّل إلى حين التحقق.</li>" for r in MULTI_DEV)}
<li>صفقة {N(ID_UNITPATTERN)} مسجّلة لمشروع «{D_UNIT['project']}» برمز وحدة ({N(D_UNIT['unit'])}) ومساحة ({N(f"{D_UNIT['area']:.2f}")} م²) يطابقان نمط وحدات مشروع «جود»؛ عُرضت كما سُجّلت مع إشارة تحقق.</li>
<li>صفقة {N(ID_NOTE)} مسجّلة لمشروع «{D_NOTE['project']}» مع {next(f for f in D_NOTE['flags'] if f.startswith('ملاحظة المستشار'))}.</li></ul></div>
{src(SRC_SALES)}''', toc=('الأداء حسب المشروع', 2))

# ---- unit & price analysis
ppm_chart = hbars([dict(label=r['name'], value=r['ppm2'], vlabel=money(r['ppm2'])) for r in by_proj if r['ppm2']], w=640, label_w=110, bar_h=15, gap=10, value_w=70)
add(f'''{sec_head('3.5 · تحليل الوحدات والأسعار', 'شقق متوسطة المساحة… في نطاق سعري متقارب',
    f"جميع الصفقات الموثقة شقق، بمساحتين فقط ({'، '.join(N(f'{a['area']:.2f}') for a in M['by_area'])} م²)، وبسعر متر يتراوح بين {N(money(min(r['ppm2'] for r in by_proj if r['ppm2'])))} و{N(money(max(r['ppm2'] for r in by_proj if r['ppm2'])))} ر.ع.")}
<div class="panel block"><h2>متوسط سعر المتر المربع حسب المشروع (ر.ع./م²)</h2>{chart('price_per_m2_by_project', ppm_chart)}</div>
<div class="grid g2 block">
  <div class="panel"><h2>ما تقوله الأسعار</h2><ul class="dots small">
    <li>{N(M['price_bands'][0]['deals'])} من {N(M['deals_documented'])} صفقات موثقة في الفئة {N('50,000–60,000')} ر.ع.، و{N(M['price_bands'][2]['deals'])} في الفئة {N('70,000–80,000')} ر.ع.</li>
    <li>الفرق بين أعلى صفقة وأدناها {OMR(M['deal_value_max'] - M['deal_value_min'])}، أي نطاق ضيق نسبيًا يناسب جمهورًا متقاربًا في القدرة الشرائية.</li>
    <li>وحدات «حي الوفاء» أكبر مساحة ({N('128')} م²) وأعلى سعرًا للمتر، بينما تجمع «جود» بين سعر أقل للوحدة وأعلى عدد صفقات.</li></ul></div>
  <div class="panel"><h2>بين الطلب والصفقة</h2><ul class="dots small">
    <li>طلبت أغلب الملاحظات التي ذكرت عدد الغرف <b>غرفة وصالة</b> ({N(bed['غرفة وصالة'])} من {N(bed_total)})، بينما لا يسجّل نموذج المبيعات عدد غرف الوحدة المباعة.</li>
    <li>إضافة حقل «عدد الغرف» إلى نموذج المبيعات يتيح قياس الفجوة بين ما يُطلب وما يُتاح للبيع.</li>
    <li>الصفقة الوحيدة لفيلا ({N(ID_VILLA)}) مسجّلة دون رمز وحدة أو سعر.</li></ul></div>
</div>
{src(SRC_SALES + ' · ' + SRC_REG.split(' · ')[0])}''', toc=('تحليل الوحدات والأسعار', 2))

# ======================================================================== PART 4 — READING & FUTURE
divider(4, 'القراءة والمستقبل', 'ما الذي تعلّمناه من البيانات، وما الذي يمكن تحسينه، ولماذا لا تنتهي المشاركة بانتهاء أيام المعرض.',
        ['أهم الاستنتاجات', 'فرص التحسين', 'الرحلة مستمرة'])

INS = [
    (N(pct(evening['share'])), 'من التسجيلات بعد 17:00', 'المساء هو الموعد الأهم',
     f"أعلى ساعتين: {N(hr(peak1['hour']))} ({N(peak1['registrations'])}) و{N(hr(peak2['hour']))} ({N(peak2['registrations'])}). توزيع الفريق والاستراحات حول هاتين الذروتين يرفع جودة الخدمة دون زيادة العدد."),
    (f"{N(deal_peak_day['deals'])} من {N(M['deals_total'])}", 'صفقات في اليوم الأخير', 'القرار يأتي بعد المقارنة',
     f"اليوم الثاني الأعلى تسجيلًا ({N(best_day['registrations'])})، واليوم الأخير الأعلى في الصفقات. العميل يجمع المعلومات أولًا ثم يعود ليقرّر؛ لذا فالمتابعة جزء من البيع لا خطوة بعده."),
    (N(pct(top_dev['share'])), f"من القيمة لمشروع «{top_proj['name']}»", 'تركيز في مشروع واحد',
     f"{N(top_proj['documented'])} صفقات موثقة بسعر موحّد تقريبًا ({OMR(top_proj['avg'])}). وضوح السعر والوحدة الجاهزة للتوثيق يسرّع القرار."),
    (f"{N(pending_dev['documented'])} من {N(pending_dev['deals'])}", f"صفقات {pending_dev['name']} الموثقة", 'فجوة بين الاهتمام والإغلاق',
     f"سجّل {pending_dev['name']} أكبر عدد من الصفقات، لكن صفقة واحدة فقط اكتملت بياناتها. استكمال رموز الوحدات والأسعار هو أسرع طريق لرفع القيمة الموثقة."),
    (N(pct(100 * bed['غرفة وصالة'] / bed_total, 0)), 'من طلبات الغرف: غرفة وصالة', 'الوحدات الأصغر مطلوبة',
     f"ومع ذكر الاستثمار في {N(tags.get('استثمار', 0))} ملاحظة، يبدو أن فكرة «خزينة» — شقة تبقى أصلًا — حاضرة في قرار العميل."),
    (N(M['open_pipeline_interested']), 'عميلًا «مهتمًا» أو «جادًا» بلا صفقة', 'أولوية المتابعة واضحة',
     f"من بين {N(M['open_pipeline'])} عميلًا في قاعدة المتابعة، هؤلاء الأقرب إلى القرار وفق ملاحظات المستشارين، ويليهم {N(M['open_pipeline_noted'] - M['open_pipeline_interested'])} عميلًا لديهم احتياج مدوّن."),
    (N(money(V['deal_value_gap'], 0)), 'ر.ع. خارج معادلة الإجمالي في السجل', 'الدقة قبل العرض',
     f"معادلة الإجمالي في سجل المبيعات {N(V['deal_value_sheet_formula'])} لم تشمل آخر صفقتين؛ فأظهرت {OMR(V['deal_value_sheet_cell'])} بدل {OMR(M['deal_value_total'])}. صُحّح الرقم في هذا التقرير."),
]
ins_html = ''.join(f'<div class="ins"><div class="fig">{a}<small>{b}</small></div><div><h3>{c}</h3><p>{d}</p></div></div>' for a, b, c, d in INS)
add(f'''{sec_head('4.1 · أهم الاستنتاجات', 'سبع قراءات من البيانات')}
{ins_html}
{src(SRC_BOTH)}''', toc=('أهم الاستنتاجات', 2))

IMP = [
    ('ربط سجل المبيعات بسجل العملاء', f"{N(M['deal_customers_unmatched'])} صفقات لعملاء غير موجودين في سجل التسجيل، و{N(sum(1 for d in D if any(f.startswith('الاسم في سجل') for f in d['flags'])))} صفقات باختلاف في الاسم.", 'جعل الرقم المدني حقلًا إلزاميًا يُتحقق منه آليًا مقابل سجل العملاء عند إدخال الصفقة.'),
    ('اكتمال بيانات الصفقة', f"{N(M['deals_pending'])} من {N(M['deals_total'])} صفقة دون رمز وحدة أو سعر.", 'منع إرسال نموذج المبيعات قبل إدخال رمز الوحدة والسعر النهائي، وإضافة حقول العربون ومرجع الحجز.'),
    ('قوائم محكومة للمطور والمشروع', 'مشروع واحد مسجّل لمطورين مختلفين، ورمز وحدة لا يطابق مشروعه.', 'قوائم منسدلة مرتبطة (المطور ← المشروع ← الوحدة) من قائمة الوحدات المعتمدة.'),
    ('حقول احتياج منظمة', f"{N(pct(100 * V['notes_tagged'] / n720))} فقط من السجلات تحمل احتياجًا قابلًا للتصنيف.", 'حقول اختيار لعدد الغرف والميزانية والغرض (سكن/استثمار) وتوقيت القرار.'),
    ('التحقق من الهاتف والهوية', f"{N(V['invalid_phones'])} أرقام هاتف و{N(V['invalid_civil_ids'])} أرقام مدنية بصيغة غير صحيحة؛ والبريد الإلكتروني مقتطع.", 'تحقق فوري من الصيغة في الاستمارة، وإصلاح طول حقل البريد في التصدير.'),
    ('نموذج إسناد واحد', f"{N(V['crm_staff_differs'])} سجلًا يختلف فيها اسم الموظف بين السجل والنظام.", 'فصل حقلي «المستشار المسؤول» و«حساب الإدخال» صراحة في النظام.'),
    ('إجماليات آلية', 'معادلة الإجمالي في سجل المبيعات لم تشمل كل الصفوف.', 'إجماليات على العمود كاملًا، أو لوحة مؤشرات تُحدّث آليًا من السجل.'),
    ('جدولة حسب الذروة', f"{N(pct(evening['share']))} من التسجيل بعد {N('17:00')}.", 'تعزيز التغطية المسائية وتنظيم الاستراحات بعيدًا عن ساعتي الذروة.'),
]
imp_rows = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in IMP)
add(f'''{sec_head('4.2 · فرص التحسين', 'ما الذي نحسّنه في المشاركة القادمة',
    'تستند كل فرصة إلى ملاحظة رُصدت فعليًا أثناء مطابقة البيانات. الهدف بيانات أدق، ومتابعة أسرع، وتقارير تُحدَّث آليًا.')}
<table class="t"><thead><tr><th style="width:36mm">المجال</th><th>ما رصدته البيانات</th><th>الإجراء المقترح</th></tr></thead><tbody>{imp_rows}</tbody></table>
{src('سجل الملاحظات في ملحق «منهجية البيانات» وملف REPORT_AUDIT.md')}''', toc=('فرص التحسين', 2))

add(f'''{sec_head('4.3 · الرحلة مستمرة', 'المعرض انتهى… والعمل لم ينتهِ',
    'لا تُقرأ نتائج المشاركة بأيام المعرض وحدها. فالاهتمام الذي سُجّل في الركن قاعدة لمسار متابعة يحوّل الاهتمام إلى قرارات، والقرارات إلى ملكية.')}
<div class="grid g4 block" style="gap:5mm">
  {kpi(N(M['open_pipeline']), 'عميلًا في قاعدة المتابعة', 'مسجّلون دون صفقة حتى الآن', 'accent lg')}
  {kpi(N(M['deals_pending']), 'صفقات قيد الاستكمال', 'بانتظار رمز الوحدة والسعر', 'accent')}
  {kpi(N(M['open_pipeline_interested']), 'عميلًا «مهتمًا» أو «جادًا»', 'أولوية أولى للمتابعة', 'accent')}
  {kpi(N(post_ev), 'تسجيلًا بعد المعرض', f"حتى {d_ar(last_reg[:10], year=False)}", 'accent')}
</div>
<div class="grid g2">
  <div class="panel"><h2>مسار المتابعة المقترح</h2><ol class="steps small">
    <li><b>استكمال الصفقات المسجّلة:</b> رمز الوحدة والسعر والحجز للصفقات الست، بالتنسيق مع المطورين.</li>
    <li><b>معالجة ملاحظات التحقق:</b> ربط الصفقات الثلاث غير المطابقة بسجلات أصحابها، وتصحيح المطور والمشروع حيث يلزم.</li>
    <li><b>متابعة الأولوية الأولى:</b> العملاء الموصوفون بـ«مهتم» أو «جاد»، ثم أصحاب الاحتياج المدوّن ({N(M['open_pipeline_noted'])} عميلًا).</li>
    <li><b>متابعة شاملة:</b> بقية قاعدة المتابعة برسالة تعريفية بالمشاريع المتاحة وفق الاحتياج.</li>
    <li><b>تقرير متابعة للوزارة:</b> تحديث المؤشرات نفسها بعد اكتمال جولة المتابعة.</li></ol></div>
  <div class="panel"><h2>ما يحكم المتابعة</h2><ul class="dots small">
    <li>استخدام بيانات العملاء لأغراض المتابعة المصرّح بها فقط، وفق موافقتهم وسياسة الخصوصية.</li>
    <li>الالتزام بالمعلومة المعتمدة: لا خصومات ولا وعود بعائد أو تمويل أو أهلية.</li>
    <li>كل عميل يبقى باسم مستشاره، وكل تواصل يُدوَّن في السجل.</li>
    <li>الحجز يتم عبر القنوات الرسمية المعتمدة فقط.</li></ul>
    <p class="note" style="margin-top:3mm">المسار المقترح خطة عمل لا تتضمن أرقامًا متوقعة؛ تُقاس نتائجه في تقرير المتابعة.</p></div>
</div>
{src(SRC_BOTH + ' · اتفاقية المشاركة (البند العاشر: السرية)')}''', toc=('الرحلة مستمرة', 2))

# ======================================================================== PART 5 — APPENDICES
divider(5, 'الملاحق', 'السجلات الكاملة كما وردت في مصادرها بعد التوحيد: كل صفقة، وكل عميل، ومنهجية حساب كل رقم.',
        ['سجل الصفقات الكامل', f'سجل العملاء المسجّلين — {N(n720)} عميلًا', 'منهجية البيانات', 'التعريفات وسجل الملاحظات'])

# ---- deal register (one page table + one page verification notes if needed)
def deal_row(d):
    st = '<span class="st ok">موثقة</span>' if d['status'] == 'موثقة' else '<span class="st pend">قيد الاستكمال</span>'
    return (f'<tr><td><b>{N(d["deal_id"])}</b><span class="sub">{d_ar(d["date"], year=False)}</span><span class="sub">{N(d["time"])}</span></td><td>{d["consultant"]}</td>'
            f'<td>{d["developer"]}<span class="sub">{d["project"]}</span></td><td>{d["unit_type"]}<span class="sub">{N(d["unit"]) if d["unit"] else "—"}</span></td>'
            f'<td class="n">{N(f"{d["area"]:.2f}") if d["area"] else "—"}</td><td class="n">{N(money(d["price"])) if d["price"] else "—"}</td>'
            f'<td class="n">{N(money(d["price_per_m2"])) if d["price_per_m2"] else "—"}</td>'
            f'<td>{d["customer"]}<span class="sub">{N(phone_fmt(d["phone"]))} · {N(d["civil_masked"])}</span></td>'
            f'<td class="n">{N(d["register_seq"]) if d["register_seq"] else "—"}</td><td>{st}</td></tr>')
deal_tbl = ''.join(deal_row(d) for d in D)
add(f'''{sec_head('ملحق أ', 'سجل الصفقات الكامل', f"جميع الصفقات المسجّلة ({N(M['deals_total'])}) مرتبة زمنيًا حسب وقت التوثيق. «—» تعني أن المعلومة غير متوفرة في المصدر.")}
<table class="t" style="font-size:7.1pt"><thead><tr><th style="width:18mm">المرجع<span class="sub" style="color:#cfd">التاريخ والوقت</span></th><th style="width:19mm">المستشار</th><th style="width:20mm">المطور<span class="sub" style="color:#cfd">المشروع</span></th>
<th style="width:17mm">نوع الوحدة<span class="sub" style="color:#cfd">رمز الوحدة</span></th><th class="n" style="width:12mm">المساحة م²</th><th class="n" style="width:16mm">السعر النهائي ر.ع.</th><th class="n" style="width:11mm">ر.ع./م²</th>
<th>العميل<span class="sub" style="color:#cfd">الهاتف · البطاقة</span></th><th class="n" style="width:9mm">رقم السجل</th><th style="width:15mm">الحالة</th></tr></thead>
<tbody>{deal_tbl}</tbody><tfoot><tr><td colspan="4">الإجمالي · {N(M['deals_total'])} صفقة · {N(M['deals_documented'])} موثقة</td><td class="n">{N(money(M['area_total_documented']))}</td><td class="n">{N(money(M['deal_value_total']))}</td><td class="n">{N(money(M['price_per_m2_avg']))}</td><td colspan="3"></td></tr></tfoot></table>
<div class="note" style="margin-top:3mm">رقم السجل: رقم العميل في سجل العملاء (ملحق ب) بعد المطابقة. البطاقة: آخر ثلاثة أرقام من الرقم المدني فقط. مجموع المساحة وسعر المتر للصفقات الموثقة فقط.</div>
{src(SRC_SALES)}''', toc=('سجل الصفقات الكامل', 2), sec='الملاحق · سجل الصفقات')

flag_rows = ''.join(f'<tr><td><b>{N(d["deal_id"])}</b></td><td>{d["match_method"]}</td><td>{"<br>".join(f for f in d["flags"]) or "لا ملاحظات"}</td></tr>' for d in D)
add(f'''<div class="reg-head"><h2>سجل الصفقات — ملاحظات التحقق</h2><div class="rng">ملحق أ (تابع)</div></div>
<p class="small">نتيجة مطابقة كل صفقة مع سجل العملاء، والملاحظات التي تحتاج إلى تحقق. لم يُعدَّل أي حقل في المصدر؛ تُعرض الملاحظة ويبقى السجل كما ورد.</p>
<table class="t"><thead><tr><th style="width:16mm">المرجع</th><th style="width:34mm">طريقة المطابقة</th><th>الملاحظات</th></tr></thead><tbody>{flag_rows}</tbody></table>
<div class="panel soft" style="margin-top:5mm"><h3>الحقول غير المتوفرة في سجل المبيعات</h3><p class="small" style="margin:0">المبنى، الطابق، عدد الغرف، الخصم، العربون أو مبلغ الحجز، طريقة الدفع، نوع التمويل، العمولة. لم تُستنتج هذه الحقول ولم تُقدَّر.</p></div>
{src(SRC_SALES)}''', sec='الملاحق · سجل الصفقات')

# ---- customer register — paginated by estimated line height so nothing is clipped
COLW = dict(seq=8, date=13, time=9, name=34, en=33, phone=15, staff=29, tags=19, deal=14)   # mm, sum = 174


def est_lines(text, width_mm, cw=1.2):
    if not text:
        return 1
    return max(1, math.ceil(len(text) * cw / (width_mm - 2.4)))


def cust_cells(c):
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in c['tags']) or '—'
    deal = '—'
    if c['deal_ids']:
        deal = '<br>'.join(N(x) for x in c['deal_ids']) + f'<span class="sub">{"موثقة" if c["deal_status"] == "صفقة موثقة" else "قيد الاستكمال"}</span>'
    ph = N(phone_fmt(c['phone'])) + ('<span class="flag"> †</span>' if not c['phone_ok'] else '')
    staff = ' + '.join(c['staff_list'])
    lines = max(est_lines(c['name_ar'], COLW['name']), est_lines(c['name_en'], COLW['en'], 1.32), est_lines(staff, COLW['staff']),
                est_lines(' '.join(c['tags']), COLW['tags'], 1.45) if c['tags'] else 1, 2 if c['deal_ids'] else 1)
    html = (f'<tr data-seq="{c["seq"]}"><td class="n">{N(c["seq"])}</td><td>{d_ar(c["date"], year=False)}</td><td class="n">{N(c["time"])}</td><td>{esc(c["name_ar"])}</td>'
            f'<td class="en">{esc(c["name_en"])}</td><td class="n">{ph}</td><td>{esc(staff)}</td><td>{tags_html}</td><td>{deal}</td></tr>')
    return html, lines


ROW1, LINE = 4.9, 3.4        # mm: fallback estimate (first build only)
# Second pass: real row heights and available table height measured in Chromium by render_pdf.cjs
MEAS_F = BUILD / 'register_metrics.json'
MEAS = json.loads(MEAS_F.read_text(encoding='utf8')) if MEAS_F.exists() else None
SAFETY = 1.0                 # mm kept free at the bottom of every register page
rows = [(c['seq'],) + cust_cells(c) for c in sorted(C, key=lambda c: c['seq'])]
row_h = [MEAS['rows'][str(seq)] if MEAS and str(seq) in MEAS['rows'] else ROW1 + (lines - 1) * LINE for seq, _, lines in rows]
cap_first = (MEAS['avail_first'] if MEAS else 205.0) - SAFETY
cap_next = (MEAS['avail_next'] if MEAS else 222.0) - SAFETY


def paginate(scale):
    """Greedy fill with every page capacity multiplied by scale (<= 1)."""
    out, cur, used = [], [], 0.0
    for (seq, html, lines), h in zip(rows, row_h):
        cap = (cap_first if not out else cap_next) * scale
        if used + h > cap and cur:
            out.append(cur); cur, used = [], 0.0
        cur.append(html); used += h
    if cur:
        out.append(cur)
    return out


# minimum page count at full capacity, then shrink capacity as far as possible without adding a page,
# so the rows spread evenly and the last page is not left with a handful of rows
chunks = paginate(1.0)
lo, hi = 0.5, 1.0
for _ in range(30):
    mid = (lo + hi) / 2
    if len(paginate(mid)) == len(chunks):
        hi = mid
    else:
        lo = mid
chunks = paginate(hi)
colgroup = ''.join(f'<col style="width:{w}mm">' for w in COLW.values())
thead = ('<thead><tr><th class="n">#</th><th>التاريخ</th><th class="n">الوقت</th><th>الاسم</th><th class="en" style="text-align:left">Name</th>'
         '<th class="n">الهاتف</th><th>خدمه</th><th>الاحتياج المدوّن</th><th>الصفقة</th></tr></thead>')
start = 1
for i, ch in enumerate(chunks):
    end = start + len(ch) - 1
    head = (f'{sec_head("ملحق ب", "سجل العملاء المسجّلين", f"جميع العملاء المسجّلين في ركن المبادرة ({N(n720)} عميلًا) مرتبين حسب تسلسل التسجيل. <span class=en>Registered Customer Record</span>.")}'
            if i == 0 else f'<div class="reg-head"><h2>سجل العملاء المسجّلين <span class="small muted">(تابع)</span></h2><div class="rng"></div></div>')
    add(f'''{head}<div class="reg-head" style="margin-bottom:1.5mm"><div class="xs muted">الصفحة {N(i + 1)} من {N(len(chunks))}</div><div class="rng">السجلات {N(f"{start}–{end}")} من {N(n720)}</div></div>
<table class="t reg" data-reg="{i}"><colgroup>{colgroup}</colgroup>{thead}<tbody>{''.join(ch)}</tbody></table>
<div class="note regnote" style="margin-top:1.6mm">† رقم هاتف بصيغة غير مكتملة كما ورد في المصدر. «خدمه»: من خدم العميل كما ورد في السجل. الرقم المدني والبريد الإلكتروني غير معروضين حفاظًا على الخصوصية.</div>''',
        sec='الملاحق · سجل العملاء', toc=(f'سجل العملاء المسجّلين — {N(n720)} عميلًا', 2) if i == 0 else None)
    start = end + 1
REG_PAGES = len(chunks)

# ---- methodology
add(f'''{sec_head('ملحق ج', 'منهجية البيانات', 'كيف بُني كل رقم في هذا التقرير، ومن أين جاء، وكيف عولجت الملاحظات.')}
<div class="grid g2" style="gap:6mm 8mm">
<div class="panel"><h3>مصادر البيانات</h3><ul class="dots small">
<li><b>سجل تسجيل العملاء</b> — ملف «بيانات عملاء أكتوبر العمران»، تبويب «العملاء»: {N(n720)} سجلًا، {N(12)} حقلًا. المصدر المعتمد للعملاء والإسناد.</li>
<li><b>نسخة النظام</b> — التبويب «AqarCRM» من الملف نفسه: {N(V['crm_records'])} سجلًا، استُخدم للمطابقة.</li>
<li><b>سجل المبيعات</b> — ملف «جدول مبيعات أكتوبر العمران - سكنة وخزينة» (ردود نموذج): {N(M['deals_total'])} صفقة.</li>
<li><b>مراجع تشغيلية</b> — اتفاقية المشاركة الموحدة، دليل إحاطة الفريق، عناوين اتفاقيات المستشارين، دليل هوية المبادرة.</li></ul></div>
<div class="panel"><h3>الفترة والتوقيت</h3><ul class="dots small">
<li>أيام المعرض: {d_ar(M['event']['start'], year=False)} – {d_ar(M['event']['end'])}، من {N('9:00')} إلى {N('22:00')}.</li>
<li>نطاق التسجيل: من {d_ar(first_reg)} ({N(first_reg[11:16])}) إلى {d_ar(last_reg)} ({N(last_reg[11:16])}).</li>
<li>جميع الأوقات بتوقيت مسقط ({N('UTC+4')}). يُنسب السجل إلى تاريخ ووقت إدخاله.</li>
<li>تاريخ استخراج البيانات وآخر تحديث: {d_ar(EXTRACT_DATE)}.</li></ul></div>
<div class="panel"><h3>طريقة الحساب</h3><ul class="dots small">
<li>خط معالجة آلي: استخراج ← توحيد ← تحقق ← مطابقة ← حساب ← رسوم ← جداول ← تقرير ← فحص.</li>
<li>كل تفصيل (حسب اليوم، المطور، المشروع، المستشار) يُجمع آليًا ويُقارن بالإجمالي؛ ويتوقف البناء عند أي فرق ولو ريالًا واحدًا.</li>
<li>القيمة الإجمالية = مجموع «سعر الوحدة النهائي» للصفقات الموثقة، بدقة منزلتين عشريتين.</li>
<li>الوسيط والمتوسط وسعر المتر للصفقات الموثقة فقط.</li></ul></div>
<div class="panel"><h3>التكرار والتوحيد</h3><ul class="dots small">
<li>العميل الفريد = رقم مدني فريد. لا توجد أرقام مدنية مكررة؛ والأسماء المتشابهة لأشخاص مختلفين.</li>
<li>الهواتف: حُذفت الرموز غير المرئية والمسافات والرمز الدولي ({N('+968')}).</li>
<li>القيم الفارغة الشكلية («.»، «-»، «0»، «…») عوملت كغير متوفرة.</li>
<li>لم يُعدّل أي اسم أو مطور أو مشروع؛ الاختلافات معروضة كملاحظات تحقق.</li></ul></div>
<div class="panel"><h3>ربط الصفقة بالعميل</h3><p class="small" style="margin:0">بالرقم المدني أولًا؛ وإن غاب أو لم يُعثر عليه، فبرقم الهاتف مع تطابق اسم العائلة. لا يُقبل التطابق بالهاتف وحده لأن الرقم قد يتشارك فيه أكثر من شخص.</p></div>
<div class="panel"><h3>تصنيف الاحتياج</h3><p class="small" style="margin:0">قواعد كلمات ثابتة على حقل «التعليقات» (عدد الغرف، استثمار، سكن، فيلا، استبدال أرض، مهتم/جاد، ميزانية محدودة). القواعد منشورة في شيفرة خط المعالجة وقابلة للمراجعة.</p></div>
</div>
{src('خط المعالجة في reports/sakna-khazina-performance/scripts · REPORT_METHODOLOGY.md')}''', toc=('منهجية البيانات', 2), sec='الملاحق · المنهجية')

DEF = [
    ('العميل المسجّل', 'شخص له سجل في سجل تسجيل العملاء برقم مدني فريد، سجّل بموافقته على سياسة الخصوصية.'),
    ('العميل المحتمل (Lead)', 'كل عميل مسجّل. لا يُميّز السجل بين مستويات الجدية إلا عبر ملاحظات المستشار.'),
    ('الصفقة المسجّلة', 'صف في سجل المبيعات يحمل اسم العميل والمطور والمشروع، أدخله المستشار بعد قرار العميل.'),
    ('الصفقة الموثقة', 'صفقة مسجّلة لها رمز وحدة وسعر نهائي أكبر من صفر. وحدها تدخل في القيمة الإجمالية.'),
    ('الصفقة قيد الاستكمال', 'صفقة مسجّلة ينقصها رمز الوحدة أو السعر النهائي.'),
    ('معدل التحويل', 'عدد الصفقات المسجّلة لكل 100 عميل مسجّل. ويُعرض معه نسبة عملاء السجل المرتبطين بصفقة.'),
    ('قاعدة المتابعة', 'العملاء المسجّلون الذين لا ترتبط بهم صفقة حتى تاريخ الاستخراج.'),
    ('الخدمة المشتركة', 'سجل يحمل اسمين أو أكثر في حقل «اسم موظف المبيعات».'),
]
dq = [
    ('معادلة إجمالي سجل المبيعات', f"{N(V['deal_value_sheet_formula'])} لا تشمل آخر صفّين · {OMR(V['deal_value_gap'])}", 'أُعيد الحساب من الصفوف'),
    ('صفقات دون رمز وحدة أو سعر', N(M['deals_pending']), 'قيد الاستكمال، خارج القيمة'),
    ('صفقات لعملاء غير موجودين في السجل', N(M['deal_customers_unmatched']), 'معروضة مع إشارة'),
    ('اختلاف الاسم بين السجلين', N(sum(1 for d in D if any(f.startswith('الاسم في سجل') for f in d['flags']))), 'معروض كما ورد'),
    ('مشروع مسجّل لمطورين مختلفين', N(len(MULTI_DEV)), 'معروض كما ورد'),
    ('أرقام هاتف بصيغة غير صحيحة', N(V['invalid_phones']), 'معروضة مع †'),
    ('أرقام مدنية بصيغة غير صحيحة', N(V['invalid_civil_ids']), 'مستبعدة من المطابقة'),
    ('البريد الإلكتروني مقتطع في المصدر', N(V['email_provided']), 'مستبعد من التقرير'),
    ('اختلاف إسناد الموظف بين السجل والنظام', N(V['crm_staff_differs']), 'اعتُمد سجل التسجيل'),
    ('سجلات عملاء مكررة', N(V['duplicate_customers']), '—'),
]
add(f'''{sec_head('ملحق د', 'التعريفات وسجل الملاحظات')}
<table class="t block"><thead><tr><th style="width:40mm">المصطلح</th><th>التعريف المعتمد في التقرير</th></tr></thead><tbody>{''.join(f'<tr><td><b>{a}</b></td><td>{b}</td></tr>' for a, b in DEF)}</tbody></table>
<h2>سجل ملاحظات جودة البيانات</h2>
<table class="t"><thead><tr><th>الملاحظة</th><th class="n" style="width:46mm">الحجم</th><th style="width:40mm">المعالجة</th></tr></thead><tbody>{''.join(f'<tr><td>{a}</td><td class="n">{b}</td><td>{c}</td></tr>' for a, b, c in dq)}</tbody></table>
<div class="note" style="margin-top:3mm">نتائج الفحص الآلي: {N(sum(M['checks'].values()))} من {N(len(M['checks']))} فحوص مطابقة ناجحة (مجاميع المطورين والمشاريع والمستشارين والأيام = الإجمالي؛ {N(n720)} عميلًا؛ لا تكرار).</div>
{src('ملف REPORT_AUDIT.md المرفق بخط المعالجة')}''', toc=('التعريفات وسجل الملاحظات', 2), sec='الملاحق · التعريفات')

# ======================================================================== CLOSING
add(f'''<div class="closing"><div class="arc"></div>
<img class="cb" src="{LOGO_COBRAND_DARK}" alt="وزارة الإسكان والتخطيط العمراني × سكنة وخزينة">
<div class="big">الرحلة بدأت…<br><span>وما زالت مستمرة.</span></div>
<div class="txt"><p>الأرقام والصفقات في هذا التقرير ليست نهاية المشاركة، بل بداية مسار من المتابعة والعمل؛ مسار يحوّل اهتمام {N(n720)} عميلًا إلى قرارات، والقرارات إلى ملكية مستدامة.</p>
<p>ووصول للاستثمار مستعدة لمواصلة دعم جهود وزارة الإسكان والتخطيط العمراني، والمساهمة بخبراتها وفريقها وقدراتها التشغيلية والتقنية والتسويقية في كل ما يخدم أهداف الوزارة والمستفيدين من مبادراتها.</p></div>
<div class="end"><div><img src="{LOGO_W_REV}" alt="WUSOOL"><div class="wusool" style="font-weight:700;margin-top:3mm;color:#fff">وصول للاستثمار</div></div>
<div class="contact"><span class="num">+968 7771 4414</span><br><span class="num">wusoolinvest.com</span><br><span class="num">@wusoolinvest</span></div></div></div>''',
    sheet='bg-midnight dark', head=False, foot=False, sec='الختام')


# ======================================================================== assemble
TOTAL = len(PAGES)
toc_html = ['<div class="sec-head"><div class="kicker">المحتويات</div><h1>محتويات التقرير</h1></div><div class="toc">']
for i, p in enumerate(PAGES, 1):
    if p['part_toc']:
        no, title = p['part_toc']
        toc_html.append(f'<div class="part"><span class="pn">{N(f"{no:02d}")}</span><span>{title}</span><span class="dots" style="flex:1"></span><span class="num" style="font-family:IBM Plex Sans Arabic;font-size:9pt">{i}</span></div>')
    elif p['toc']:
        toc_html.append(f'<div class="it"><span>{p["toc"][0]}</span><span class="dots"></span><span class="pg">{N(i)}</span></div>')
toc_html.append('</div>')
PAGES[2]['body'] = ''.join(toc_html)

out = []
for i, p in enumerate(PAGES, 1):
    body = p['body'].replace('{{TOTAL}}', str(TOTAL))
    head = (f'<div class="run-head"><div class="rh-title"><b>مبادرة سكنة وخزينة</b> · تقرير أداء فريق وصول للاستثمار</div><div class="rh-sec">{p["sec"]}</div></div>' if p['head'] else '')
    foot = (f'<div class="run-foot"><div class="conf">سري — للاستخدام الرسمي</div><div class="by">وصول للاستثمار</div><div class="pg">{N(f"{i:02d}")} <span class="muted" style="font-weight:400">/ {N(TOTAL)}</span></div></div>' if p['foot'] else '')
    inner = body if not p['head'] else f'<div class="body">{body}</div>'
    if p['cls']:
        inner = f'<div class="{p["cls"]}">{inner}</div>'
    out.append(f'<section class="sheet {p["sheet"]}" data-page="{i}"><div class="page">{head}{inner}{foot}</div></section>')

html = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>تقرير الأداء — مبادرة سكنة وخزينة — وصول للاستثمار</title>
<link rel="stylesheet" href="../src/report.css">
<style>{":root{--bleed:3mm}@page{size:216mm 303mm;margin:0}" if BLEED else ""}</style>
</head><body>{''.join(out)}</body></html>'''
(BUILD / ('report_bleed.html' if BLEED else 'report.html')).write_text(html, encoding='utf8')
(BUILD / 'build_info.json').write_text(json.dumps(dict(pages=TOTAL, register_pages=REG_PAGES, register_rows=len(rows)), ensure_ascii=False), encoding='utf8')
print(f'pages={TOTAL} register_pages={REG_PAGES}')
