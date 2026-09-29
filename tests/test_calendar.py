import json
import unittest
from datetime import date
from icalendar import Calendar
from filter_calendar import ROOT, Rules, filter_ics
from weekly import generate


def event(title, extra='', uid='a'):
    return f'BEGIN:VEVENT\r\nUID:{uid}\r\nDTSTAMP:20260901T100000Z\r\nDTSTART;TZID=Europe/Paris:20260929T090000\r\nDTEND;TZID=Europe/Paris:20260929T110000\r\nSUMMARY:{title}\r\n{extra}END:VEVENT\r\n'


def calendar(body):
    return ('BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Test//FR\r\n'+body+'END:VCALENDAR\r\n').encode()


class FilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = Rules(json.loads((ROOT/'rules.json').read_text(encoding='utf-8')))

    def classify(self, title, description=''):
        return self.rules.classify({'SUMMARY':title, 'DESCRIPTION':description})[0]

    def test_allowed(self):
        for title in ['Socio-économie de la mobilité', 'Organisation des transports publics',
                      'Articulation transports aménagement', 'MASYT', 'ACOST',
                      'Analyse et conception des systèmes de transport', 'Économie des réseaux avancée',
                      'Analyse données de mobilité', 'Méthodes photo-vidéo',
                      "Réseaux et fabrique de l’espace public", 'Anglais professionnel',
                      "Voyage d&#39;étude", 'Atelier', 'Controverses sociotechniques']:
            with self.subTest(title=title): self.assertEqual(self.classify(title), 'keep')

    def test_excluded(self):
        for title in ['Ingénierie du trafic', 'Système de transport de marchandises',
                      'Systèmes de mobilité dans le monde', 'Conception systèmes transport et mobilité',
                      'Économie des transports avancée', 'Paysage', 'SIG',
                      'Gestion et maintenance', 'Réseaux et limites planétaires',
                      'Infrastructures et risques', 'Modèles sociotechniques',
                      'Circulations transnationales', 'Modèles économiques et sobriété']:
            with self.subTest(title=title): self.assertEqual(self.classify(title), 'exclude')

    def test_livret_common_and_ris(self):
        for title in ['UE1 Réseaux et territoires', 'UE 1 Réseaux et Territoires',
                      'UE3 Planification, gouvernance, politiques et action publique',
                      'UE4 Usages, usagers, pratiques sociales',
                      'UE2 Transitions socio-écologiques et environnementales',
                      'Transitions', 'Transition', 'UE4 Professionnalisation',
                      "EC1 Séminaire d’accompagnement", 'EC2 Stage et mémoire']:
            with self.subTest(title=title): self.assertEqual(self.classify(title), 'keep')
        for title in ['UE1 Réseaux et limites planétaires', 'UE2 Gestion et maintenance',
                      'UE3 Infrastructures et risques', 'High tech / low tech',
                      'UE4 Modèles sociotechniques des infrastructures : entre high tech et low tech',
                      'UE5 Circulations transnationales', 'UE6 Modèles économiques et sobriété']:
            with self.subTest(title=title): self.assertEqual(self.classify(title), 'exclude')
        self.assertEqual(self.classify('UE1 Réseaux et territoires', 'Cours RIS'), 'exclude')
        self.assertEqual(self.classify('UE3'), 'unknown')

    def test_precedence_and_unknown(self):
        self.assertEqual(self.classify('ACOST', 'Ingénierie du trafic'), 'exclude')
        self.assertEqual(self.classify('Séance', 'Méthodes photo-vidéo'), 'keep')
        self.assertEqual(self.classify('Semaine transversale 1'), 'unknown')
        self.assertEqual(self.classify('Économie des transports débutants'), 'unknown')
        self.assertEqual(self.classify('SIG analyse données de mobilité'), 'keep')

    def test_stable_and_roundtrip(self):
        raw=calendar(event('ACOST', 'SEQUENCE:3\r\nDESCRIPTION:Texte\\nligne 2\r\n')+event('SIG',uid='b'))
        a, report=filter_ics(raw,self.rules)
        b, _=filter_ics(raw,self.rules)
        self.assertEqual(a,b)
        events=Calendar.from_ical(a).walk('VEVENT')
        self.assertEqual(len(events),1)
        self.assertEqual(str(events[0]['UID']),'a')
        self.assertEqual(int(events[0]['SEQUENCE']),3)
        self.assertEqual(str(events[0]['DTSTART'].params['TZID']),'Europe/Paris')

    def test_excluded_exception_removes_series(self):
        raw=calendar(event('ACOST','RRULE:FREQ=WEEKLY;COUNT=3\r\n')+event('SIG','RECURRENCE-ID;TZID=Europe/Paris:20261006T090000\r\n'))
        encoded, report=filter_ics(raw,self.rules)
        self.assertEqual(len(Calendar.from_ical(encoded).walk('VEVENT')),0)
        self.assertTrue(report[0]['series_blocked'])

    def test_bad_input(self):
        for raw in [b'<html>error</html>',calendar(''),b'BEGIN:VCALENDAR\r\n']:
            with self.assertRaises(ValueError): filter_ics(raw,self.rules)

    def test_week_and_escaping(self):
        raw=calendar(event('ACOST </script><script>alert(1)</script>', 'RRULE:FREQ=WEEKLY;COUNT=3\r\n'))
        page,_=generate(raw,self.rules,date(2026,9,29))
        self.assertNotIn('ACOST </script>',page)
        data=json.loads(page.split('id="data">')[1].split('</script>')[0])
        self.assertEqual(len(data['events']),3)
        self.assertEqual(data['monday'],'2026-09-28')
        self.assertIn('+02:00',data['events'][0]['start'])


if __name__=='__main__': unittest.main()
