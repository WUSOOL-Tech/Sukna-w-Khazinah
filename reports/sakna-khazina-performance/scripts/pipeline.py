#!/usr/bin/env python3
"""Raw data -> normalize -> validate -> reconcile -> calculate.

Inputs  (data/raw/, git-ignored — personal data):
  customers_sheet_alomlaa.json   «بيانات عملاء أكتوبر العمران» tab «العملاء»  (canonical customer register)
  customers_sheet_aqarcrm.json   same file, tab «AqarCRM»                      (CRM mirror, used for reconciliation)
  sales_form_responses.json      «جدول مبيعات أكتوبر العمران - سكنة وخزينة»   (sales form = deal register)
  team_contracts.json            consultant contract titles from Drive        (team roster)

Outputs:
  data/processed/customers.csv, deals.csv   (git-ignored — personal data)
  data/aggregates/metrics.json               (git-ignored — names consultants)
  data/aggregates/validation.json            (counts only)

Every figure printed in the report is read from metrics.json; nothing is typed by hand.
"""
import csv, json, re, statistics, sys
from collections import Counter, defaultdict, OrderedDict
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC, AGG = ROOT / 'data/raw', ROOT / 'data/processed', ROOT / 'data/aggregates'

EVENT_NAME = 'أكتوبر العمران 2026'
EVENT_START, EVENT_END = date(2026, 10, 5), date(2026, 10, 8)   # contract §1 + team briefing
EVENT_OPEN_H, EVENT_CLOSE_H = 9, 22                              # 9:00–22:00 (contract §2)
AR_DAYS = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
JUNK = {'', '.', '..', '.-', '-', '|', 'ء', 'ظ', '…', '0', 'لايوجد'}


def clean(s):
    s = (s or '').replace('‬', '').replace('‪', '').replace('‏', '').replace('‎', '')
    return re.sub(r'\s+', ' ', s).strip()


def arnorm(s):
    """Spelling-insensitive key for Arabic name comparison (hamza forms, taa marbuta, alif maqsura)."""
    s = re.sub('[أإآ]', 'ا', clean(s))
    return s.replace('ة', 'ه').replace('ى', 'ي')


def short_name(full):
    """'أروى بنت ياسر الخروصي' -> 'أروى الخروصي' (first + family name, as used in the register)."""
    t = clean(full).split()
    return t[0] + ' ' + t[-1] if len(t) > 1 else clean(full)


def norm_phone(raw):
    d = re.sub(r'\D', '', clean(raw))
    if d.startswith('968') and len(d) == 11:
        d = d[3:]
    return d


def phone_valid(d):
    return len(d) == 8 and d[0] in '79'


def civil_valid(c):
    return bool(re.fullmatch(r'\d{6,9}', c or ''))


def mask_civil(c):
    return '•••' + c[-3:] if civil_valid(c) else '—'


# ---------------------------------------------------------------- interest tags (rule-based, from the free-text note)
TAG_RULES = [
    ('غرفتان أو 3 غرف', r'غرفتين او ٣|غرفتين أو ٣'),
    ('3 غرف', r'ثلاث غرف|٣ غرف|3 غرف'),
    ('غرفتان', r'غرفتين|٢ غرف|2 غرف|٢ غرفة|غرف وصالة 2|غرفة وصالة 2'),
    ('غرفة وصالة', r'غرفة وصالة|غرفه وصاله|غرفة وصاله|غرفه وصالة|بغرفة|لغرفة|شقة غرفة|شقه غرفة|استثمار \+ غرفة'),
    ('فيلا', r'فيلا|ڤلة'),
    ('استبدال أرض', r'تبديل ارض|استبدال ارض|يستبدل|قطعة ارض بشقة'),
    ('استثمار', r'استثمار'),
    ('سكن', r'للسكن|شقة للسكن|^سكن$|شقه سكن'),
    ('ميزانية محدودة', r'ميزانية منخفضة|منخضة'),
    ('مهتم', r'مهتم|ومتهم|هتم|مهمم'),
    ('جاد', r'جاد|وحاد|بشده'),
]


def interest_tags(note):
    tags = []
    for tag, rx in TAG_RULES:
        if re.search(rx, note):
            if tag == 'غرفتان' and 'غرفتان أو 3 غرف' in tags:
                continue
            if tag == '3 غرف' and 'غرفتان أو 3 غرف' in tags:
                continue
            tags.append(tag)
    return tags


# ---------------------------------------------------------------- load
def load_values(name):
    return json.loads((RAW / name).read_text(encoding='utf8'))['values']


def build_customers():
    rows = load_values('customers_sheet_alomlaa.json')
    crm = load_values('customers_sheet_aqarcrm.json')
    hdr, rows = rows[0], rows[1:]
    crm_by_seq = {r[0]: r for r in crm[1:]}
    out = []
    for r in rows:
        r = r + [''] * (12 - len(r))
        seq = int(r[0])
        ts = datetime.strptime(r[1], '%Y-%m-%d %H:%M:%S')
        c = crm_by_seq.get(r[0])
        note = clean(r[9])
        note_clean = '' if note in JUNK else note
        staff = clean(r[8])
        out.append(OrderedDict(
            seq=seq, registered_at=ts.isoformat(sep=' '), date=ts.date().isoformat(), time=ts.strftime('%H:%M'),
            hour=ts.hour, name_ar=clean(r[2]), name_en=clean(r[3]), civil_id=clean(r[4]),
            id_expiry=clean(r[5]), phone_raw=r[6], phone=norm_phone(r[6]), email=clean(r[7]),
            staff=staff, staff_list=[clean(x) for x in staff.split('+') if clean(x)],
            crm_account=clean(c[6]) if c else '', crm_name=clean(c[2]) if c else '', crm_phone=norm_phone(c[5]) if c else '',
            crm_ts=c[1] if c else '', crm_civil=clean(c[4]) if c else '',
            note_raw=note, note=note_clean, tags=interest_tags(note_clean),
            broker=clean(r[10]), consent=clean(r[11]),
            in_event=EVENT_START <= ts.date() <= EVENT_END,
        ))
    return hdr, out


def to_num(s):
    s = clean(s).replace(',', '')
    try:
        return float(s)
    except ValueError:
        return None


def build_deals(customers):
    raw = json.loads((RAW / 'sales_form_responses.json').read_text(encoding='utf8'))
    rows = [r for r in raw['values'][1:] if r and clean(r[0])]
    by_civil = {c['civil_id']: c for c in customers}
    by_phone = defaultdict(list)
    for c in customers:
        by_phone[c['phone']].append(c)
    recs = []
    for r in rows:
        r = r + [''] * (12 - len(r))
        ts = datetime.strptime(r[0], '%m/%d/%Y %H:%M:%S')
        unit = clean(r[5]); unit = '' if unit in JUNK else unit
        area = to_num(r[6]); area = area if area else None
        price = to_num(r[7]); price = price if price else None
        civil = clean(r[9]); civil = '' if civil in JUNK else civil
        phone = norm_phone(r[10])
        name = clean(r[8])
        recs.append(dict(ts=ts, consultant_full=clean(r[1]), developer=clean(r[2]), project=clean(r[3]),
                         unit_type=clean(r[4]), unit=unit, area=area, price=price, name=name,
                         civil_id=civil, phone=phone, note='' if clean(r[11]) in JUNK else clean(r[11])))
    recs.sort(key=lambda d: d['ts'])
    deals = []
    phone_count = Counter(d['phone'] for d in recs)
    proj_devs = defaultdict(Counter)
    for d in recs:
        proj_devs[d['project']][d['developer']] += 1
    for i, d in enumerate(recs, 1):
        flags = []
        # ---- link to the customer register: civil ID first, then phone + family name
        m, method = None, 'غير مطابق'
        if d['civil_id'] and d['civil_id'] in by_civil:
            m, method = by_civil[d['civil_id']], 'الرقم المدني'
        elif d['phone'] in by_phone:
            fam = d['name'].split()[-1]
            cands = [c for c in by_phone[d['phone']] if arnorm(c['name_ar']).split()[-1] == arnorm(fam)]
            if len(cands) == 1:
                m, method = cands[0], 'الهاتف + اسم العائلة'
            else:
                flags.append('رقم الهاتف مسجّل في السجل لعميل آخر؛ لم يُطابَق')
        if m:
            rn, dn = arnorm(m['name_ar']).split(), arnorm(d['name']).split()
            if rn[-1] != dn[-1] or rn[0] != dn[0]:
                flags.append(f'الاسم في سجل التسجيل «{m["name_ar"]}»')
        documented = bool(d['unit'] and d['price'])
        if not documented:
            flags.append('رمز الوحدة والسعر غير مستكملين في نموذج المبيعات')
        if phone_count[d['phone']] > 1:
            flags.append('رقم الهاتف نفسه مسجّل لصفقة أخرى')
        if len(proj_devs[d['project']]) > 1:
            others = [k for k in proj_devs[d['project']] if k != d['developer']]
            flags.append(f'المشروع نفسه مسجّل في صفقات أخرى للمطور «{"، ".join(others)}»')
        if d['unit'].startswith('A01/') and d['project'] != 'جود':
            flags.append('رمز الوحدة ومساحتها يطابقان نمط وحدات مشروع «جود»؛ يلزم التحقق من المطور والمشروع')
        if d['note']:
            flags.append(f'ملاحظة المستشار: «{d["note"]}»')
        if not (EVENT_START <= d['ts'].date() <= EVENT_END):
            flags.append('وُثّقت بعد أيام المعرض')
        deals.append(OrderedDict(
            deal_id=f'SK-{i:02d}', submitted_at=d['ts'].strftime('%Y-%m-%d %H:%M'), date=d['ts'].date().isoformat(),
            time=d['ts'].strftime('%H:%M'), consultant_full=d['consultant_full'], consultant=short_name(d['consultant_full']),
            developer=d['developer'], project=d['project'], unit_type=d['unit_type'], unit=d['unit'],
            area=d['area'], price=d['price'], price_per_m2=round(d['price'] / d['area'], 2) if documented and d['area'] else None,
            customer=d['name'], civil_id=d['civil_id'], civil_masked=mask_civil(d['civil_id']), phone=d['phone'],
            status='موثقة' if documented else 'قيد الاستكمال',
            register_seq=m['seq'] if m else None, match_method=method, register_staff=m['staff'] if m else '',
            flags=flags,
        ))
    return raw, deals


# ---------------------------------------------------------------- validation & reconciliation
def validate(customers, deals, raw_sales):
    v = OrderedDict()
    n = len(customers)
    v['customer_records'] = n
    v['customer_seq_complete'] = sorted(c['seq'] for c in customers) == list(range(1, n + 1))
    v['unique_civil_ids'] = len({c['civil_id'] for c in customers})
    v['invalid_civil_ids'] = sum(not civil_valid(c['civil_id']) for c in customers)
    phones = Counter(c['phone'] for c in customers)
    v['unique_phones'] = len(phones)
    v['shared_phone_numbers'] = sum(1 for p, k in phones.items() if k > 1)
    v['records_on_shared_phone'] = sum(k for p, k in phones.items() if k > 1)
    v['invalid_phones'] = sum(not phone_valid(c['phone']) for c in customers)
    v['phones_with_country_code'] = sum(c['phone_raw'].strip().startswith('+') for c in customers)
    names = Counter(c['name_ar'] for c in customers)
    v['repeated_names_distinct_people'] = sum(k for k in names.values() if k > 1)
    v['repeated_name_groups'] = sum(1 for k in names.values() if k > 1)
    v['duplicate_customers'] = n - v['unique_civil_ids']
    v['short_names_two_words'] = sum(len(c['name_ar'].split()) == 2 for c in customers)
    v['email_field_filled'] = sum(bool(c['email']) for c in customers)
    v['email_provided'] = sum(len(c['email']) > 1 for c in customers)
    v['email_cut_at_12_14_chars'] = sum(11 <= len(c['email']) <= 14 for c in customers)
    v['email_wellformed'] = sum(bool(re.fullmatch(r'[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}', c['email'])) for c in customers)
    v['id_expiry_provided'] = sum(bool(c['id_expiry']) for c in customers)
    v['notes_raw_nonempty'] = sum(bool(c['note_raw']) for c in customers)
    v['notes_meaningful'] = sum(bool(c['note']) for c in customers)
    v['notes_tagged'] = sum(bool(c['tags']) for c in customers)
    v['consent_yes'] = sum(c['consent'] == 'أوافق' for c in customers)
    v['broker_wusool'] = sum(c['broker'] == 'وصول للاستثمار' for c in customers)
    # CRM mirror reconciliation
    v['crm_records'] = sum(bool(c['crm_account']) for c in customers)
    v['crm_same_civil'] = sum(c['crm_civil'] == c['civil_id'] for c in customers)
    v['crm_same_timestamp'] = sum(c['crm_ts'] == c['registered_at'] for c in customers)
    v['crm_same_name'] = sum(c['crm_name'] == c['name_ar'] for c in customers)
    v['crm_same_phone_normalized'] = sum(c['crm_phone'] == c['phone'] for c in customers)
    v['crm_phone_format_diffs'] = sum(norm_phone(c['phone_raw']) == c['crm_phone'] and c['phone_raw'] != c['crm_phone'] for c in customers)
    v['crm_staff_differs'] = sum(c['crm_account'] != c['staff'] for c in customers)
    # deals
    v['deal_records'] = len(deals)
    v['deal_ids_unique'] = len({d['deal_id'] for d in deals}) == len(deals)
    keys = Counter((d['developer'], d['project'], d['unit'], d['customer']) for d in deals)
    v['duplicate_deals'] = sum(k - 1 for k in keys.values() if k > 1)
    units = Counter(d['unit'] for d in deals if d['unit'])
    v['unit_codes_reused'] = sum(1 for k in units.values() if k > 1)
    v['deals_documented'] = sum(d['status'] == 'موثقة' for d in deals)
    v['deals_pending'] = sum(d['status'] != 'موثقة' for d in deals)
    v['deals_matched_to_register'] = sum(d['register_seq'] is not None for d in deals)
    v['deals_unmatched'] = sum(d['register_seq'] is None for d in deals)
    v['deal_customers_distinct'] = len({(d['customer'], d['civil_id']) for d in deals})
    total = round(sum(d['price'] or 0 for d in deals), 2)
    sheet = raw_sales['sheet_total_cell']
    v['deal_value_total_recomputed'] = total
    v['deal_value_sheet_cell'] = sheet['value']
    v['deal_value_sheet_formula'] = sheet['formula']
    v['deal_value_gap'] = round(total - sheet['value'], 2)
    v['deals_flagged'] = sum(bool([f for f in d['flags'] if not f.startswith('رمز الوحدة والسعر')]) for d in deals)
    return v


# ---------------------------------------------------------------- metrics
def money_sum(xs):
    return round(sum(xs), 2)


def calc(customers, deals, v):
    M = OrderedDict()
    n = len(customers)
    days = sorted({c['date'] for c in customers})
    event_days = [d for d in days if EVENT_START.isoformat() <= d <= EVENT_END.isoformat()]
    M['event'] = dict(name=EVENT_NAME, start=EVENT_START.isoformat(), end=EVENT_END.isoformat(),
                      days=(EVENT_END - EVENT_START).days + 1, open_hour=EVENT_OPEN_H, close_hour=EVENT_CLOSE_H,
                      operating_hours=((EVENT_END - EVENT_START).days + 1) * (EVENT_CLOSE_H - EVENT_OPEN_H))
    M['customers_total'] = n
    M['customers_in_event'] = sum(c['in_event'] for c in customers)
    M['customers_post_event'] = n - M['customers_in_event']
    M['first_registration'] = min(c['registered_at'] for c in customers)
    M['last_registration'] = max(c['registered_at'] for c in customers)
    M['avg_per_event_day'] = round(M['customers_in_event'] / len(event_days), 1)
    M['avg_per_operating_hour'] = round(M['customers_in_event'] / M['event']['operating_hours'], 1)

    # ---- by day
    deals_by_day = defaultdict(list)
    for d in deals:
        deals_by_day[d['date']].append(d)
    by_day = []
    for dstr in sorted(set(days) | set(deals_by_day)):
        dd = date.fromisoformat(dstr)
        regs = [c for c in customers if c['date'] == dstr]
        dl = deals_by_day.get(dstr, [])
        hours = Counter(c['hour'] for c in regs)
        peak = max(hours.items(), key=lambda kv: (kv[1], -kv[0])) if hours else (None, 0)
        by_day.append(dict(date=dstr, weekday=AR_DAYS[dd.weekday()], in_event=EVENT_START <= dd <= EVENT_END,
                           registrations=len(regs), deals=len(dl), deals_documented=sum(x['status'] == 'موثقة' for x in dl),
                           value=money_sum(x['price'] or 0 for x in dl), peak_hour=peak[0], peak_count=peak[1],
                           first=min((c['time'] for c in regs), default=None), last=max((c['time'] for c in regs), default=None)))
    M['by_day'] = by_day

    # ---- by hour (event days only, 9..21) and heatmap
    ev = [c for c in customers if c['in_event']]
    hc = Counter(c['hour'] for c in ev)
    M['by_hour'] = [dict(hour=h, registrations=hc.get(h, 0)) for h in range(EVENT_OPEN_H, EVENT_CLOSE_H + 1)]
    top = sorted(hc.items(), key=lambda kv: (-kv[1], kv[0]))
    M['peak_hours'] = [dict(hour=h, registrations=k) for h, k in top[:4]]
    blocks = OrderedDict([('الفترة الصباحية (9:00–12:59)', range(9, 13)), ('فترة الظهيرة (13:00–16:59)', range(13, 17)),
                          ('الفترة المسائية (17:00–22:00)', range(17, 23))])
    M['by_block'] = [dict(label=k, registrations=sum(hc.get(h, 0) for h in r), share=round(100 * sum(hc.get(h, 0) for h in r) / len(ev), 1)) for k, r in blocks.items()]
    M['heatmap'] = {dstr: [sum(1 for c in ev if c['date'] == dstr and c['hour'] == h) for h in range(EVENT_OPEN_H, EVENT_CLOSE_H + 1)] for dstr in event_days}

    # ---- team attribution (field attribution in the «العملاء» tab)
    solo = Counter(); shared = Counter(); deals_by_c = defaultdict(list)
    for c in customers:
        if len(c['staff_list']) == 1:
            solo[c['staff_list'][0]] += 1
        else:
            for s in c['staff_list']:
                shared[s] += 1
    for d in deals:
        deals_by_c[d['consultant']].append(d)
    people = sorted(set(solo) | set(shared) | set(deals_by_c), key=lambda p: (-(solo[p] + shared[p]), p))
    M['team'] = []
    for p in people:
        dl = deals_by_c.get(p, [])
        doc = [x for x in dl if x['status'] == 'موثقة']
        involved = solo[p] + shared[p]
        M['team'].append(dict(name=p, solo=solo[p], shared=shared[p], involved=involved,
                              share=round(100 * involved / n, 1), deals=len(dl), deals_documented=len(doc),
                              value=money_sum(x['price'] for x in doc),
                              avg=round(money_sum(x['price'] for x in doc) / len(doc), 2) if doc else None,
                              deals_per_100=round(100 * len(dl) / involved, 1) if involved and dl else None))
    M['records_solo'] = sum(len(c['staff_list']) == 1 for c in customers)
    M['records_shared'] = n - M['records_solo']
    M['names_in_register'] = len(people)
    # ---- contracted team (Drive contract titles) vs names that appear in the booth records
    roster = json.loads((RAW / 'team_contracts.json').read_text(encoding='utf8'))
    alias = {v_: k for k, v_ in roster.get('register_aliases', {}).items()}
    names_in = {t['name'] for t in M['team']}
    M['roster'] = []
    for c in roster['contracts']:
        sn = alias.get(c['name'], short_name(c['name']))
        M['roster'].append(dict(no=c['no'], role=c['role'], name=c['name'], short=sn, in_records=sn in names_in))
    contracted_short = {r['short'] for r in M['roster']}
    for t in M['team']:
        t['contracted'] = t['name'] in contracted_short
    M['consultants_contracted'] = sum(r['role'] == 'مستشار عقاري' for r in M['roster'])
    M['contracts_total'] = len(M['roster'])
    M['contracted_in_records'] = sum(r['in_records'] for r in M['roster'])
    M['supporting_names'] = sum(not t['contracted'] for t in M['team'])
    M['records_with_contracted'] = sum(any(s in contracted_short for s in c['staff_list']) for c in customers)
    M['crm_accounts'] = [dict(name=k, registrations=v_) for k, v_ in Counter(c['crm_account'] for c in customers).most_common()]

    # ---- interest (rule-based tags from consultant notes)
    tagc = Counter(t for c in customers for t in c['tags'])
    M['interest_tags'] = [dict(tag=t, count=k) for t, k in tagc.most_common()]
    bed = OrderedDict((k, tagc.get(k, 0)) for k in ['غرفة وصالة', 'غرفتان', 'غرفتان أو 3 غرف', '3 غرف'])
    M['bedroom_mentions'] = [dict(label=k, count=v_) for k, v_ in bed.items()]
    M['notes_meaningful'] = v['notes_meaningful']
    M['notes_tagged'] = v['notes_tagged']
    M['intent_investment'] = tagc.get('استثمار', 0)
    M['intent_residence'] = tagc.get('سكن', 0)
    M['intent_interested'] = sum(1 for c in customers if 'مهتم' in c['tags'] or 'جاد' in c['tags'])
    M['intent_land_swap'] = tagc.get('استبدال أرض', 0)
    M['intent_villa'] = tagc.get('فيلا', 0)

    # ---- deals
    doc = [d for d in deals if d['status'] == 'موثقة']
    prices = sorted(d['price'] for d in doc)
    total = money_sum(prices)
    M['deals_total'] = len(deals)
    M['deals_documented'] = len(doc)
    M['deals_pending'] = len(deals) - len(doc)
    M['deal_value_total'] = total
    M['deal_value_avg'] = round(total / len(doc), 2)
    M['deal_value_median'] = round(statistics.median(prices), 2)
    M['deal_value_min'] = prices[0]
    M['deal_value_max'] = prices[-1]
    M['area_total_documented'] = round(sum(d['area'] for d in doc), 2)
    M['price_per_m2_avg'] = round(total / M['area_total_documented'], 2)
    M['deal_customers_matched'] = v['deals_matched_to_register']
    M['deal_customers_unmatched'] = v['deals_unmatched']
    M['conv_deal_records_per_100'] = round(100 * len(deals) / n, 2)
    M['conv_registered_with_deal'] = round(100 * v['deals_matched_to_register'] / n, 2)
    M['conv_documented_per_100'] = round(100 * len(doc) / n, 2)
    M['open_pipeline'] = n - v['deals_matched_to_register']
    M['open_pipeline_interested'] = sum(1 for c in customers if ('مهتم' in c['tags'] or 'جاد' in c['tags']) and c['seq'] not in {d['register_seq'] for d in deals})
    M['open_pipeline_noted'] = sum(1 for c in customers if c['tags'] and c['seq'] not in {d['register_seq'] for d in deals})

    def group(key):
        g = defaultdict(list)
        for d in deals:
            g[d[key]].append(d)
        res = []
        for k, dl in g.items():
            dd = [x for x in dl if x['status'] == 'موثقة']
            val = money_sum(x['price'] for x in dd)
            res.append(dict(name=k, deals=len(dl), documented=len(dd), pending=len(dl) - len(dd), value=val,
                            share=round(100 * val / total, 1) if total else 0, avg=round(val / len(dd), 2) if dd else None,
                            projects=sorted({x['project'] for x in dl}), developers=sorted({x['developer'] for x in dl}),
                            unit_types=dict(Counter(x['unit_type'] for x in dl)),
                            areas=sorted({x['area'] for x in dd}), min=min((x['price'] for x in dd), default=None),
                            max=max((x['price'] for x in dd), default=None),
                            ppm2=round(val / sum(x['area'] for x in dd), 2) if dd else None,
                            consultants=sorted({x['consultant'] for x in dl})))
        return sorted(res, key=lambda r: (-r['value'], -r['deals'], r['name']))
    M['by_developer'] = group('developer')
    M['by_project'] = group('project')
    M['by_consultant'] = group('consultant')
    M['by_unit_type'] = [dict(name=k, deals=v_) for k, v_ in Counter(d['unit_type'] for d in deals).most_common()]
    M['by_area'] = [dict(area=k, deals=v_) for k, v_ in sorted(Counter(d['area'] for d in doc).items())]
    bands = [(50000, 60000), (60000, 70000), (70000, 80000)]
    M['price_bands'] = [dict(label=f'{lo:,}–{hi:,}', lo=lo, hi=hi, deals=sum(lo <= p < hi for p in prices),
                             value=money_sum(p for p in prices if lo <= p < hi)) for lo, hi in bands]
    M['deal_days'] = [dict(date=b['date'], weekday=b['weekday'], deals=b['deals'], documented=b['deals_documented'], value=b['value'])
                      for b in by_day if b['deals']]
    M['developers_count'] = len(M['by_developer'])
    M['projects_count'] = len(M['by_project'])
    M['consultants_with_deals'] = len(M['by_consultant'])
    return M


def reconcile(M, v):
    """Hard checks: every breakdown must sum back to the totals. Fails the build otherwise."""
    checks = OrderedDict()
    t = M['deal_value_total']
    for k in ('by_developer', 'by_project', 'by_consultant'):
        checks[f'{k}: value sum = total'] = money_sum(r['value'] for r in M[k]) == t
        checks[f'{k}: deal count sum = total'] = sum(r['deals'] for r in M[k]) == M['deals_total']
    checks['by_day: value sum = total'] = money_sum(b['value'] for b in M['by_day']) == t
    checks['by_day: deals sum = total'] = sum(b['deals'] for b in M['by_day']) == M['deals_total']
    checks['by_day: registrations sum = 720'] = sum(b['registrations'] for b in M['by_day']) == M['customers_total']
    checks['by_hour: sum = in-event registrations'] = sum(h['registrations'] for h in M['by_hour']) == M['customers_in_event']
    checks['heatmap: sum = in-event registrations'] = sum(sum(r) for r in M['heatmap'].values()) == M['customers_in_event']
    checks['solo + shared = 720'] = M['records_solo'] + M['records_shared'] == M['customers_total']
    checks['price bands cover documented deals'] = sum(b['deals'] for b in M['price_bands']) == M['deals_documented']
    checks['customer count = 720'] = M['customers_total'] == 720
    checks['customer civil IDs unique'] = v['unique_civil_ids'] == 720
    checks['CRM mirror: same civil IDs'] = v['crm_same_civil'] == 720
    checks['no duplicate deals'] = v['duplicate_deals'] == 0
    checks['documented + pending = deals'] = M['deals_documented'] + M['deals_pending'] == M['deals_total']
    return checks


def write_csv(path, rows, fields):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: ('، '.join(r[k]) if isinstance(r[k], list) else r[k]) for k in fields})


def main():
    PROC.mkdir(parents=True, exist_ok=True); AGG.mkdir(parents=True, exist_ok=True)
    _, customers = build_customers()
    raw_sales, deals = build_deals(customers)
    deal_seq = defaultdict(list)
    for d in deals:
        if d['register_seq']:
            deal_seq[d['register_seq']].append(d)
    for c in customers:
        dl = deal_seq.get(c['seq'], [])
        c['deal_ids'] = [d['deal_id'] for d in dl]
        c['deal_status'] = ('صفقة موثقة' if any(d['status'] == 'موثقة' for d in dl) else 'صفقة قيد الاستكمال') if dl else ''
        c['phone_ok'] = phone_valid(c['phone'])
    v = validate(customers, deals, raw_sales)
    M = calc(customers, deals, v)
    checks = reconcile(M, v)
    write_csv(PROC / 'customers.csv', customers, ['seq', 'registered_at', 'name_ar', 'name_en', 'civil_id', 'phone', 'phone_ok', 'email',
                                                  'staff', 'crm_account', 'note_raw', 'tags', 'deal_ids', 'deal_status', 'in_event', 'consent'])
    write_csv(PROC / 'deals.csv', deals, ['deal_id', 'submitted_at', 'consultant_full', 'developer', 'project', 'unit_type', 'unit', 'area',
                                          'price', 'price_per_m2', 'customer', 'civil_id', 'phone', 'status', 'register_seq', 'match_method', 'flags'])
    (PROC / 'customers.json').write_text(json.dumps(customers, ensure_ascii=False, indent=1), encoding='utf8')
    (PROC / 'deals.json').write_text(json.dumps(deals, ensure_ascii=False, indent=1), encoding='utf8')
    M['validation'] = v
    M['checks'] = checks
    M['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    (AGG / 'metrics.json').write_text(json.dumps(M, ensure_ascii=False, indent=1), encoding='utf8')
    (AGG / 'validation.json').write_text(json.dumps(dict(validation=v, checks=checks), ensure_ascii=False, indent=1), encoding='utf8')
    bad = [k for k, ok in checks.items() if not ok]
    for k, ok in checks.items():
        print(('PASS ' if ok else 'FAIL ') + k)
    if bad:
        sys.exit('reconciliation failed: ' + '; '.join(bad))


if __name__ == '__main__':
    main()
