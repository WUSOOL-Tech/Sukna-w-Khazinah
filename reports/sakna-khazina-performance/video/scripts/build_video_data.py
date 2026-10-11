#!/usr/bin/env python3
"""metrics.json + voice_timing.json -> build/video_data.js (window.D, window.T) for the composition.
Every figure in the video is read from the report's metrics; scene times come from the edited narration."""
import json
from pathlib import Path

V = Path(__file__).resolve().parents[1]
R = V.parent
M = json.loads((R / 'data/aggregates/metrics.json').read_text(encoding='utf8'))
VT = json.loads((V / 'build/voice/voice_timing.json').read_text(encoding='utf8'))

VO = 2.8        # visual-only lead before the voice starts (logo reveal)
LEAD = 0.45     # each scene's visuals start this much before its narration
HOLD = 3.6      # end-card hold after the last word

sc = VT['scenes']
T = []
for i, s in enumerate(sc):
    t0 = 0.0 if i == 0 else VO + s['voice_start'] - LEAD
    t1 = (VO + sc[i + 1]['voice_start'] - LEAD) if i + 1 < len(sc) else VO + VT['duration'] + HOLD
    T.append(dict(id=s['id'], t0=round(t0, 3), t1=round(t1, 3), v0=round(VO + s['voice_start'], 3), v1=round(VO + s['voice_end'], 3)))

ev = [b for b in M['by_day'] if b['in_event']]
best = max(ev, key=lambda b: b['registrations'])
tags = {t['tag']: t['count'] for t in M['interest_tags']}
bed = {b['label']: b['count'] for b in M['bedroom_mentions']}
proj = {r['name']: r for r in M['by_project']}
D = dict(
    customers=M['customers_total'], in_event=M['customers_in_event'], post_event=M['customers_post_event'],
    duplicates=M['validation']['duplicate_customers'], consent_pct=round(100 * M['validation']['consent_yes'] / M['customers_total']),
    days=M['event']['days'], hours=M['event']['operating_hours'], consultants=M['consultants_contracted'],
    by_day=[dict(wd=b['weekday'], d=int(b['date'][8:]), n=b['registrations'], ev=b['in_event'], best=b is best) for b in M['by_day']],
    by_hour=[dict(h=h['hour'], n=h['registrations']) for h in M['by_hour']],
    peak_hours=[p['hour'] for p in M['peak_hours'][:2]],
    evening_share=M['by_block'][2]['share'],
    bed=[dict(l=k, n=bed[k]) for k in ['غرفة وصالة', 'غرفتان', '3 غرف']],
    bed_total=sum(bed.values()), tagged=M['validation']['notes_tagged'],
    invest=tags.get('استثمار', 0), resid=tags.get('سكن', 0),
    deals=M['deals_total'], documented=M['deals_documented'], pending=M['deals_pending'],
    value=M['deal_value_total'], avg=M['deal_value_avg'],
    projects=[dict(p=r['name'], dev=r['developers'][0] if len(r['developers']) == 1 else '، '.join(r['developers']), value=r['value'], share=r['share'], n=r['documented'])
              for r in M['by_project'] if r['value'] > 0],
    deal_days=[dict(wd=x['weekday'], d=int(x['date'][8:]), n=x['deals'], doc=x['documented']) for x in M['deal_days']],
    pipeline=M['open_pipeline'], interested=M['open_pipeline_interested'],
    source='المصدر: سجلات ركن المبادرة — بيانات العملاء والمبيعات · استخراج 11 أكتوبر 2026',
)
(V / 'build').mkdir(exist_ok=True)
(V / 'build/video_data.js').write_text('window.D = ' + json.dumps(D, ensure_ascii=False) + ';\nwindow.T = ' + json.dumps(T, ensure_ascii=False)
                                        + ';\nwindow.DURATION = ' + str(T[-1]['t1']) + ';\nwindow.VO = ' + str(VO) + ';\n', encoding='utf8')
print(f'duration {T[-1]["t1"]:.2f}s')
for t in T:
    print(f"{t['id']:13s} {t['t0']:7.2f} → {t['t1']:7.2f}   voice {t['v0']:7.2f} – {t['v1']:7.2f}")
