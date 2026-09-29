"""Filtre conservateur M2 TRAME. Python 3.11+."""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import html
import json
from pathlib import Path
import re
import time
import unicodedata
from urllib.request import Request, urlopen

from icalendar import Calendar

SOURCE = 'https://calendar.google.com/calendar/ical/m2.tm.orga%40gmail.com/public/basic.ics'
ROOT = Path(__file__).resolve().parent


def normalize(text):
    text = html.unescape(str(text)).lower()
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', text).strip()


class Rules:
    def __init__(self, data):
        self.rules = {kind: [(r['id'], re.compile(r['pattern'])) for r in data[kind]]
                      for kind in ('keep', 'exclude')}

    def classify(self, event):
        fields = [normalize(event.get(k, '')) for k in ('SUMMARY', 'DESCRIPTION')]
        # Ne pas joindre les champs : éviter une correspondance artificielle.
        for kind in ('exclude', 'keep'):
            hits = [name for name, pattern in self.rules[kind]
                    if any(pattern.search(text) for text in fields)]
            if hits:
                return kind, hits
        return 'unknown', []


def filter_ics(raw, rules):
    if not raw.strip().startswith(b'BEGIN:VCALENDAR') or not raw.strip().endswith(b'END:VCALENDAR'):
        raise ValueError('Réponse incomplète ou non iCalendar')
    source = Calendar.from_ical(raw)
    if source.name != 'VCALENDAR' or str(source.get('VERSION')) != '2.0':
        raise ValueError('VCALENDAR 2.0 attendu')
    if any(c.errors for c in source.walk()):
        raise ValueError('Erreurs de parsing iCalendar')
    events = [c for c in source.subcomponents if c.name == 'VEVENT']
    if not events:
        raise ValueError('Source vide : publication bloquée')
    groups = defaultdict(list)
    for event in events:
        if not event.get('UID') or not event.get('DTSTAMP'):
            raise ValueError('VEVENT sans UID ou DTSTAMP')
        if not event.get('DTSTART') and str(event.get('STATUS')) != 'CANCELLED':
            raise ValueError('VEVENT sans DTSTART')
        groups[str(event['UID'])].append(event)
    output = deepcopy(source)
    output.subcomponents = [deepcopy(c) for c in source.subcomponents if c.name == 'VTIMEZONE']
    for key in ('X-WR-CALNAME', 'X-WR-CALDESC', 'METHOD', 'PRODID'):
        output.pop(key, None)
    output.add('PRODID', '-//TRAME//Maxime TM Filter//FR')
    output.add('X-WR-CALNAME', 'TRAME — Maxime — TM')
    output.add('X-WR-CALDESC', 'Cours attribués au profil TM de Maxime')
    output.add('METHOD', 'PUBLISH')
    report = []
    for uid, group in groups.items():
        decisions = [rules.classify(e) for e in group]
        # Une exception retirée seule serait recréée par RRULE dans le client.
        # Politique stricte : toute la série est retirée si un élément est refusé
        # ou ambigu, sauf une exception sans texte qui hérite du maître autorisé.
        masters = [i for i, e in enumerate(group) if 'RECURRENCE-ID' not in e]
        master_keep = len(masters) == 1 and decisions[masters[0]][0] == 'keep'
        for i, event in enumerate(group):
            if ('RECURRENCE-ID' in event and master_keep and decisions[i][0] == 'unknown'
                    and not normalize(event.get('SUMMARY', ''))
                    and not normalize(event.get('DESCRIPTION', ''))):
                decisions[i] = ('keep', ['inherit-master'])
        kept = all(d[0] == 'keep' for d in decisions)
        for event, (decision, reasons) in zip(group, decisions):
            report.append({'uid': uid, 'summary': str(event.get('SUMMARY', '')),
                           'start': str(event.get('DTSTART', '')), 'classification': decision,
                           'rules': reasons, 'kept': kept,
                           'series_blocked': decision == 'keep' and not kept})
            if kept:
                output.add_component(deepcopy(event))
    encoded = output.to_ical()
    Calendar.from_ical(encoded)
    return encoded, report


def download(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'TRAME-calendar-filter/1.0'}), timeout=45) as response:
                raw = response.read(20_000_001)
            if len(raw) > 20_000_000:
                raise ValueError('Source supérieure à 20 Mo')
            return raw
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(data)
    tmp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='Fichier local au lieu du téléchargement')
    parser.add_argument('--source', default=SOURCE)
    parser.add_argument('--rules', type=Path, default=ROOT / 'rules.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'public/maxime.ics')
    parser.add_argument('--report', type=Path, default=ROOT / 'audit.json')
    parser.add_argument('--allow-empty', action='store_true')
    args = parser.parse_args()
    rules = Rules(json.loads(args.rules.read_text(encoding='utf-8')))
    raw = args.input.read_bytes() if args.input else download(args.source)
    encoded, report = filter_ics(raw, rules)
    atomic_write(args.report, json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8'))
    kept = sum(r['kept'] for r in report)
    if not kept and not args.allow_empty:
        raise ValueError('Aucun cours retenu : vérifier audit.json ; ancien flux préservé')
    atomic_write(args.output, encoded)
    print(json.dumps({'total': len(report), 'kept': kept,
                      'classifications': dict(Counter(r['classification'] for r in report))}))


if __name__ == '__main__':
    main()
