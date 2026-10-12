import json
import unittest
from datetime import date, datetime
from io import BytesIO
from urllib.error import URLError

import enpc

# Structure observée sur emploidutemps.enpc.fr (données d'exemple, pas une copie du site).
PAGE = '''<html><body><table>
<tr height="30" bgcolor="#b6e0e4"><td align="center">12:30-15:30</td><td align="center">VET</td><td align="center">Grande Ruche - 80 places - PC externe</td><td align="center"></td><td align="left">&nbsp;ACOST - Analyse et conception de syst&egrave;me de transport</td></tr>
<tr height="30" bgcolor="#FFFFFF"><td align="center">12:30-15:30</td><td align="center">VET</td><td align="center">salle P 012 - 56 places- camera</td><td align="center"></td><td align="left">&nbsp;MASYT - M&eacute;thodes d'analyse</td></tr>
<tr height="30" bgcolor="#b6e0e4"><td align="center">12:30-15:30</td><td align="center">VET</td><td align="center">P 402  - 30 personnes</td><td align="center"></td><td align="left">&nbsp;MASYT - M&eacute;thodes d'analyse</td></tr>
<tr height="30" bgcolor="#FFFFFF"><td align="center">12:30-15:30</td><td align="center">VET</td><td align="center">salle P 012 - 56 places- camera</td><td align="center"></td><td align="left">&nbsp;MASYT - M&eacute;thodes d'analyse</td></tr>
<tr height="30" bgcolor="#b6e0e4"><td align="center">08:30-11:30</td><td align="center">VET</td><td align="center">salle F 207 - 34 places</td><td align="center">(Gr2)</td><td align="left">&nbsp;MASYT - Matin&Atilde;&copy;e</td></tr>
<tr height="30" bgcolor="#FFFFFF"><td align="center">13:30-15:30</td><td align="center">1A</td><td align="center">salle B 004</td><td align="center"></td><td align="left">&nbsp;1MEDP - Mod&eacute;lisation</td></tr>
</table></body></html>'''


class Response(BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): return False


def event(title, start, end):
    return {'title': title, 'start': start, 'end': end, 'allDay': False}


class EnpcTests(unittest.TestCase):
    def test_parse_rows_and_encoding(self):
        rows = enpc.parse_rows(PAGE)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0], ['12:30-15:30', 'VET', 'Grande Ruche - 80 places - PC externe', '',
                                   'ACOST - Analyse et conception de système de transport'])
        self.assertEqual(enpc.fix('MatÃ©riaux poreux'), 'Matériaux poreux')
        self.assertEqual(enpc.fix('déjà correct'), 'déjà correct')

    def test_clean_room(self):
        for raw, expected in [('salle P 203 -  1A -38 places - camera', 'P 203'), ('Grande Ruche - 80 places - PC externe', 'Grande Ruche'),
                              ('P 402  - 30 personnes', 'P 402'), ('salle P 102- 48 places - Ordinateur externe uniquement', 'P 102'),
                              ('Amphi M.F. Clugnet - 200 places', 'Amphi M.F. Clugnet'), ('P 404   10 personnes', 'P 404')]:
            with self.subTest(raw=raw): self.assertEqual(enpc.clean_room(raw), expected)

    def test_rooms_for_matches_code_and_slot(self):
        rows = enpc.parse_rows(PAGE)
        start, end = datetime(2026, 10, 14, 12, 30), datetime(2026, 10, 14, 15, 30)
        self.assertEqual(enpc.rooms_for(rows, 'ACOST', start, end), ['Grande Ruche'])
        self.assertEqual(enpc.rooms_for(rows, 'masyt', start, end), ['P 012', 'P 402'])  # sans doublon
        self.assertEqual(enpc.rooms_for(rows, 'MASYT', datetime(2026, 10, 14, 8, 30), datetime(2026, 10, 14, 11, 30)), ['F 207 (Gr2)'])
        self.assertEqual(enpc.rooms_for(rows, 'MASYT', datetime(2026, 10, 14, 16, 0), datetime(2026, 10, 14, 18, 0)), [])
        self.assertEqual(enpc.rooms_for(rows, 'OTP', start, end), [])

    def test_lookup_only_for_enpc_events(self):
        calls = []
        def opener(request, timeout):
            calls.append(request.full_url)
            return Response(PAGE.encode('utf-8'))
        rooms = enpc.Rooms(today=date(2026, 10, 12), opener=opener, pause=0)
        e = event('MASYT (ENPC)', '2026-10-14T12:30:00+02:00', '2026-10-14T15:30:00+02:00')
        self.assertEqual(rooms(e), 'P 012 · P 402')
        self.assertEqual(rooms(event('ACOST (ENPC)', '2026-10-14T12:30:00+02:00', '2026-10-14T15:30:00+02:00')), 'Grande Ruche')
        self.assertEqual(len(calls), 1)  # une seule lecture par jour
        self.assertIn('mydate=14/10/2026', calls[0])
        self.assertEqual(rooms(event('Organisation des transports publics', '2026-10-14T12:30:00+02:00', '2026-10-14T15:30:00+02:00')), '')
        self.assertEqual(rooms({**e, 'allDay': True}), '')
        self.assertEqual(rooms(event('MASYT (ENPC)', '2026-09-01T12:30:00+02:00', '2026-09-01T15:30:00+02:00')), '')  # passé : pas de requête
        self.assertEqual(len(calls), 1)

    def test_site_down_never_raises(self):
        def down(request, timeout): raise URLError('hors ligne')
        rooms = enpc.Rooms(today=date(2026, 10, 12), opener=down, pause=0)
        self.assertEqual(rooms(event('ACOST (ENPC)', '2026-10-14T12:30:00+02:00', '2026-10-14T15:30:00+02:00')), '')
        self.assertTrue(rooms.failed)

    def test_generate_adds_room_field(self):
        from filter_calendar import ROOT, Rules
        from weekly import generate
        rules = Rules(json.loads((ROOT / 'rules.json').read_text(encoding='utf-8')))
        raw = ('BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//T//FR\r\nBEGIN:VEVENT\r\nUID:a\r\nDTSTAMP:20260901T100000Z\r\n'
               'DTSTART;TZID=Europe/Paris:20261014T123000\r\nDTEND;TZID=Europe/Paris:20261014T153000\r\nSUMMARY:ACOST (ENPC)\r\n'
               'END:VEVENT\r\nEND:VCALENDAR\r\n').encode()
        page, _ = generate(raw, rules, date(2026, 10, 14), lambda e: 'Grande Ruche')
        data = json.loads(page.split('id="data">')[1].split('</script>')[0])
        self.assertEqual([e['room'] for e in data['events']], ['Grande Ruche'])
        page, _ = generate(raw, rules, date(2026, 10, 14))
        self.assertNotIn('"room"', page)


if __name__ == '__main__': unittest.main()
