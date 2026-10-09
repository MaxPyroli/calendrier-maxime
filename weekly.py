"""Produit un aperçu autonome de 25 semaines autour de la semaine choisie."""
import argparse
from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar
import recurring_ical_events

from filter_calendar import ROOT, SOURCE, Rules, atomic_write, download, filter_ics

PARIS = ZoneInfo('Europe/Paris')


def local(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=PARIS) if value.tzinfo is None else value.astimezone(PARIS)
    return datetime.combine(value, time.min, PARIS)


def generate(raw, rules, anchor):
    encoded, audit = filter_ics(raw, rules)
    monday = anchor - timedelta(days=anchor.weekday())
    start, end = monday - timedelta(weeks=12), monday + timedelta(weeks=13)
    calendar = Calendar.from_ical(encoded)
    events = []
    for event in recurring_ical_events.of(calendar).between(local(start), local(end)):
        if str(event.get('STATUS')) == 'CANCELLED':
            continue
        begin = event.decoded('DTSTART')
        finish = event.decoded('DTEND', None)
        all_day = not isinstance(begin, datetime)
        if finish is None:
            finish = begin + event.decoded('DURATION', timedelta(days=1) if all_day else timedelta())
        events.append({'title': str(event.get('SUMMARY', 'Sans titre')),
                       'location': str(event.get('LOCATION', '')),
                       'start': local(begin).isoformat(), 'end': local(finish).isoformat(),
                       'allDay': all_day})
    events.sort(key=lambda e: e['start'])
    data = {'events': events, 'monday': monday.isoformat(), 'first': start.isoformat(),
            'last': (end - timedelta(weeks=1)).isoformat(),
            'updated': datetime.now(PARIS).strftime('%d/%m/%Y à %H:%M'),
            'unknown': sum(r['classification'] == 'unknown' for r in audit),
            'kept': sum(r['kept'] for r in audit), 'total': len(audit)}
    # Le contenu distant n'est jamais interprété comme du HTML ou du JavaScript.
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = (ROOT / 'template.html').read_text(encoding='utf-8')
    return template.replace('__CALENDAR_DATA__', payload), audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--week', type=date.fromisoformat, default=datetime.now(PARIS).date())
    parser.add_argument('--output', type=Path, default=ROOT / 'index.html')
    args = parser.parse_args()
    rules = Rules(json.loads((ROOT / 'rules.json').read_text(encoding='utf-8')))
    raw = args.input.read_bytes() if args.input else download(SOURCE)
    page, audit = generate(raw, rules, args.week)
    atomic_write(ROOT / 'audit.json', json.dumps(audit, ensure_ascii=False, indent=2).encode('utf-8'))
    if not any(r['kept'] for r in audit):
        raise ValueError('Aucun événement retenu dans la source : publication bloquée')
    atomic_write(args.output, page.encode('utf-8'))
    print(json.dumps({'total': len(audit), 'kept': sum(r['kept'] for r in audit),
                      'unknown': sum(r['classification'] == 'unknown' for r in audit)}))


if __name__ == '__main__':
    main()
