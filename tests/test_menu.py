import contextlib
import io
import json
import unittest
from datetime import date, datetime
from io import BytesIO
from urllib.error import HTTPError
from zoneinfo import ZoneInfo

import menu

# Formes déduites du code public de l'appli myMRS (pas de vraies réponses du service).
PLANNING_LOGIN = [{'ZSLIBELLE': 'Restaurant A', 'PROGRAMME': [
    {'DATE': '2026-10-13', 'RECETTE': [{'TYPONAME': 'Entrée', 'RECETTELIB': 'Salade &amp; croûtons'},
                                       {'TYPONAME': 'Plat', 'RECETTELIB': 'Poulet rôti'}]},
    {'DATE': 'October, 14 2026 00:00:00', 'RECETTE': [{'TYPONAME': 'Plat', 'RECETTELIB': 'Pâtes'}]}]}]
PLANNING_SITE = {'1': {'ZSLIBELLE': 'Restaurant A', '2026-10-14': [{'TYPONAME': 'Plat', 'RECETTELIB': 'Pâtes'}],
                       '2026-10-15': [{'TYPONAME': 'Plat', 'RECETTELIB': 'Poisson'}]}}
NOW = datetime(2026, 10, 13, 11, 0, tzinfo=ZoneInfo('Europe/Paris'))


class FakeResponse(BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): return False


class MenuTests(unittest.TestCase):
    def test_parse_day(self):
        for value in ['2026-10-13', '2026-10-13T00:00:00', '13/10/2026', '13-10-2026',
                      'October, 13 2026 00:00:00', "{ts '2026-10-13 00:00:00'}"]:
            with self.subTest(value=value): self.assertEqual(menu.parse_day(value), date(2026, 10, 13))
        for value in [None, '', 'ZSLIBELLE', '2026-13-45']:
            with self.subTest(value=value): self.assertIsNone(menu.parse_day(value))

    def test_collect_merges_both_shapes_without_duplicates(self):
        merged = menu.collect(PLANNING_LOGIN, PLANNING_SITE)
        self.assertEqual(sorted(merged), [date(2026, 10, 13), date(2026, 10, 14), date(2026, 10, 15)])
        self.assertEqual(merged[date(2026, 10, 14)]['Restaurant A'], [{'type': 'Plat', 'label': 'Pâtes'}])
        self.assertEqual(merged[date(2026, 10, 13)]['Restaurant A'][0], {'type': 'Entrée', 'label': 'Salade & croûtons'})

    def test_build_drops_old_and_empty_days(self):
        merged = menu.collect(PLANNING_LOGIN)
        merged[date(2026, 9, 1)] = {'Restaurant A': [{'type': 'Plat', 'label': 'Vieux'}]}
        merged[date(2026, 10, 16)] = {'Restaurant A': []}
        data = menu.build(merged, NOW.date(), NOW)
        self.assertEqual([d['date'] for d in data['days']], ['2026-10-13', '2026-10-14'])
        self.assertEqual(data['updated'], '13/10/2026 à 11:00')
        with self.assertRaises(menu.MenuError): menu.build({}, NOW.date(), NOW)

    def test_render_escapes_remote_text(self):
        data = {'days': [{'date': '2026-10-13', 'restaurants': [{'name': 'A', 'items': [
            {'type': '', 'label': '</script><script>alert(1)</script>'}]}]}], 'updated': 'x'}
        page = menu.render(data)
        self.assertNotIn('</script><script>alert', page)
        parsed = json.loads(page.split('id="data">')[1].split('</script>')[0])
        self.assertEqual(parsed['days'][0]['restaurants'][0]['items'][0]['label'], '</script><script>alert(1)</script>')

    def test_connect_extracts_site_and_never_leaks_password(self):
        seen = []
        def opener(request, timeout):
            seen.append(request.full_url)
            return FakeResponse(json.dumps({'SUCCESS': True, 'MESINFOS': {'MESSITE': [{'SITEID': 7}], 'NOM': 'privé'},
                                            'MONPLANNING': PLANNING_LOGIN}).encode())
        site_id, planning = menu.connect('a@b.fr', 'se cret&=', opener)
        self.assertEqual((site_id, planning), (7, PLANNING_LOGIN))
        self.assertIn('password=se+cret%26%3D', seen[0])

    def test_special_characters_roundtrip(self):
        from urllib.parse import parse_qs, urlsplit
        for password in ['#abc', '$abc', '%41bc', '+abc', '"abc', "'abc", '!abc', '{abc}', 'é&=? /\\ x', '@ab:c']:
            with self.subTest(password=password):
                seen = []
                def opener(request, timeout):
                    seen.append(request.full_url)
                    return FakeResponse(b'{"SUCCESS": false}')
                with self.assertRaises(menu.MenuError): menu.connect('a@b.fr', password, opener)
                self.assertEqual(parse_qs(urlsplit(seen[0]).query)['password'], [password])

    def test_errors_do_not_contain_credentials(self):
        def refused(request, timeout):
            raise HTTPError(request.full_url, 403, 'Forbidden', {}, None)
        with self.assertRaises(menu.MenuError) as caught:
            menu.connect('a@b.fr', 'motdepasse-secret', refused)
        self.assertNotIn('motdepasse-secret', str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)

    def test_login_refused_and_bad_json(self):
        with self.assertRaises(menu.MenuError):
            menu.connect('a', 'b', lambda r, timeout: FakeResponse(b'{"SUCCESS": false}'))
        with self.assertRaises(menu.MenuError):
            menu.connect('a', 'b', lambda r, timeout: FakeResponse(b'<html>maintenance</html>'))
        site_id, _ = menu.connect('a', 'b', lambda r, timeout: FakeResponse(b'//{"success": "YES", "mesinfos": {"messite": [{"siteid": 3}]}}'))
        self.assertEqual(site_id, 3)

    def test_diagnostic_hides_personal_values(self):
        def opener(request, timeout):
            if 'getConnexion' in request.full_url:
                body = {'SUCCESS': True, 'TOKEN': 'jeton-secret', 'MONPLANNING': PLANNING_LOGIN,
                        'MESINFOS': {'NOM': 'Dupont', 'MESSITE': [{'SITEID': 7, 'SITELIBELLE': 'Site'}]}}
            else:
                body = {'SUCCESS': True, 'DATA': PLANNING_SITE}
            return FakeResponse(json.dumps(body).encode())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            menu.diagnostic('a@b.fr', 'motdepasse-secret', date(2026, 10, 13), opener)
        text = out.getvalue()
        for secret in ['Dupont', 'jeton-secret', 'motdepasse-secret', 'a@b.fr']:
            self.assertNotIn(secret, text)
        report = json.loads(text)
        self.assertIn('NOM', report['MESINFOS'])
        self.assertIn('PROGRAMME', report['MONPLANNING'][1])
        self.assertIn('semaine suivante', report)


if __name__ == '__main__': unittest.main()
