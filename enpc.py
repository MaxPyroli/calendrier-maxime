"""Salles des cours donnés à l'ENPC, lues sur https://emploidutemps.enpc.fr (un jour par page).

Seuls les événements dont l'intitulé finit par « (ENPC) » sont concernés, par exemple « ACOST (ENPC) » ou
« MASYT (ENPC) [Soutenance] » : le premier mot est le code du cours chez l'ENPC. Une panne du site ne doit
jamais bloquer la publication du calendrier : sans réponse, l'événement reste simplement sans salle.
"""
from datetime import date, datetime, timedelta
import html
import re
import sys
import time
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE = 'https://emploidutemps.enpc.fr/'
CODE = re.compile(r'^\s*([A-Za-z][A-Za-z0-9]{2,7})\b.*\(ENPC\)')


def fix(text):
    """Le site mélange UTF-8 et ISO-8859-1 : on répare « Ã© » en « é »."""
    try:
        return text.encode('latin-1').decode('utf-8') if ('Ã' in text or 'Â' in text) else text
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def parse_rows(page):
    """Lignes du jour : [créneau, département, salle, groupe, intitulé]."""
    rows = []
    for tr in re.findall(r'<tr height="30"[^>]*>(.*?)</tr>', page, re.S):
        cells = [fix(html.unescape(re.sub(r'<[^>]+>', '', c)).replace('\xa0', ' ').strip())
                 for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if len(cells) >= 5:
            rows.append(cells[:5])
    return rows


def clean_room(raw):
    """« salle P 203 -  1A -38 places - camera » devient « P 203 » ; « Grande Ruche - 80 places » devient « Grande Ruche »."""
    text = re.sub(r'^\s*salle\s+', '', raw.strip(), flags=re.I)
    text = re.split(r'\s*-\s|\s+-|\s{2,}|\s+\d+\s*(?:places|personnes)', text)[0]
    return re.sub(r'\s+', ' ', text).strip(' -')


def row_code(title):
    words = title.strip().split(' - ')[0].split()
    return words[0].upper() if words else ''


def minutes(clock):
    hours, mins = clock.split(':')
    return int(hours) * 60 + int(mins)


def rooms_for(rows, code, start, end):
    """Salles des lignes du cours `code` dont le créneau recoupe [start, end] (datetime locaux)."""
    wanted = code.upper()
    begin, finish = start.hour * 60 + start.minute, end.hour * 60 + end.minute
    found = []
    for slot, _dept, room, group, title in rows:
        if row_code(title) != wanted:
            continue
        match = re.match(r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})', slot)
        if match and not (minutes(match.group(1)) < finish and minutes(match.group(2)) > begin):
            continue
        label = clean_room(room) + (f' {group.strip()}' if group.strip() else '')
        if label.strip() and label not in found:
            found.append(label)
    return found


class Rooms:
    """Rattache une salle aux événements « (ENPC) ». Les pages sont lues à la demande, une fois par jour."""

    def __init__(self, today=None, opener=urlopen, pause=0.3):
        self.today = today or date.today()
        self.opener = opener
        self.pause = pause
        self.pages = {}
        self.failed = False
        self.found = 0

    def day(self, day):
        if day not in self.pages:
            self.pages[day] = self._download(day)
        return self.pages[day]

    def _download(self, day):
        url = f'{BASE}?code_departement=&mydate={quote(day.strftime("%d/%m/%Y"))}'
        request = Request(url, headers={'User-Agent': 'calendrier-maxime (agenda personnel M2 TRAME)'})
        try:
            time.sleep(self.pause)
            with self.opener(request, timeout=20) as response:
                return parse_rows(response.read().decode('utf-8', 'replace'))
        except (URLError, TimeoutError, OSError):
            if not self.failed:
                print('Avertissement : emploi du temps ENPC injoignable, salles non actualisées', file=sys.stderr)
            self.failed = True
            return []

    def __call__(self, event):
        """`event` : dict avec title, start, end (ISO 8601). Renvoie la salle à afficher, ou ''."""
        match = CODE.match(event['title'])
        if not match or event.get('allDay'):
            return ''
        start, end = datetime.fromisoformat(event['start']), datetime.fromisoformat(event['end'])
        if start.date() < self.today - timedelta(days=1):
            return ''  # inutile de relire le passé à chaque génération
        found = rooms_for(self.day(start.date()), match.group(1), start, end)
        self.found += bool(found)
        return ' · '.join(found)
