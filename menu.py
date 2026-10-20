"""Récupère le menu de la cantine myMRS et produit une page autonome (menu.html). Python 3.11+.

Accès lu dans MYMRS_LOGIN + MYMRS_PASSWORD (ou MYMRS_PASSWORD_HEX : le mot de passe écrit en hexadécimal,
utile s'il commence par un caractère spécial) ou, à défaut, dans MYMRS_TOKEN (jeton de l'appli, qui peut
expirer). Rien n'est jamais écrit ni affiché.
Seuls les plats sont publiés : aucune donnée de compte (nom, solde, badge) n'est conservée.
"""
import argparse
from datetime import date, datetime, timedelta
import html
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from filter_calendar import ROOT, atomic_write

PARIS = ZoneInfo('Europe/Paris')
API = 'https://www.mymrs.fr/webservices'
LOGIN = '/connexion.cfc?method=getConnexion'
PLANNING = '/menu.cfc?method=getPlanningBySite'
DATA_FILE = ROOT / 'menu.json'
DEVICE = 'DUMMY__IMEI'  # valeur envoyée par l'appli web officielle
MONTHS = {m: i for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july',
                                       'august', 'september', 'october', 'november', 'december'], 1)}


class MenuError(Exception):
    """Erreur d'affichage sûr : le message ne contient jamais d'identifiant."""


def call(path, params, opener=urlopen):
    # Les identifiants voyagent dans l'URL (comme dans l'appli officielle) :
    # on coupe la chaîne d'exceptions pour qu'ils n'apparaissent dans aucune trace.
    url = API + path + '&' + urlencode(params)
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (menu-cantine)', 'Accept': 'application/json'})
    try:
        with opener(request, timeout=30) as response:
            body = response.read().decode('utf-8-sig', 'replace')
    except HTTPError as error:
        raise MenuError(f'myMRS a répondu HTTP {error.code}') from None
    except (URLError, TimeoutError, OSError) as error:
        raise MenuError(f'myMRS injoignable ({type(error).__name__})') from None
    body = body.strip()
    if body.startswith('//'):  # préfixe de sécurité de ColdFusion
        body = body[2:]
    try:
        data = json.loads(body)
    except ValueError:
        raise MenuError('Réponse myMRS illisible (JSON attendu)') from None
    if not isinstance(data, dict):
        raise MenuError('Réponse myMRS inattendue')
    return data


def pick(data, key, default=None):
    """Lecture insensible à la casse (ColdFusion met les clés en majuscules)."""
    if isinstance(data, dict):
        for name, value in data.items():
            if str(name).upper() == key:
                return value
    return default


def truthy(value):
    return value is True or str(value).strip().lower() in {'1', 'true', 'yes', 'oui'}


def connect(login, password, opener=urlopen):
    return open_session({'login': login, 'password': password}, opener)


def connect_token(token, opener=urlopen):
    return open_session({'token': token}, opener)


def refusal(identity, data):
    text = ('Jeton refusé ou expiré par myMRS : en récupérer un nouveau (MYMRS_TOKEN)' if 'token' in identity
            else 'Connexion refusée par myMRS : vérifier MYMRS_LOGIN et MYMRS_PASSWORD')
    code = pick(data, 'EXCEPTIONTYPE')
    detail = ', '.join(filter(None, [clean(pick(data, 'EXCEPTIONMESSAGE'))[:60],
                                     f'type {code}' if code not in (None, '') else '']))
    if detail and not any(secret and secret in detail for secret in identity.values()):
        text += f' [réponse : {detail}]'
    return MenuError(text)


def open_session(identity, opener=urlopen):
    data = call(LOGIN, {**identity, 'device': DEVICE}, opener)
    if not truthy(pick(data, 'SUCCESS')):
        raise refusal(identity, data)
    sites = pick(pick(data, 'MESINFOS'), 'MESSITE') or []
    site_id = pick(sites[0], 'SITEID') if sites else None
    return site_id, pick(data, 'MONPLANNING')


def identities_from_env(environ=os.environ):
    """Accès possibles, dans l'ordre d'essai : identifiant + mot de passe (durable), puis jeton de l'appli."""
    found = []
    login = environ.get('MYMRS_LOGIN', '').strip()
    password = environ.get('MYMRS_PASSWORD', '').rstrip('\r\n')
    if environ.get('MYMRS_PASSWORD_HEX', '').strip():
        try:
            password = bytes.fromhex(environ['MYMRS_PASSWORD_HEX'].strip()).decode('utf-8')
        except ValueError:
            raise MenuError('MYMRS_PASSWORD_HEX invalide : uniquement des chiffres et lettres a-f') from None
    if login and password:
        found.append({'login': login, 'password': password})
    if environ.get('MYMRS_TOKEN', '').strip():
        found.append({'token': environ['MYMRS_TOKEN'].strip()})
    return found


def next_week_planning(site_id, today, opener=urlopen):
    """Semaine suivante : l'appli ne la demande que le vendredi soir, nous la prenons toujours."""
    friday = today - timedelta(days=today.weekday()) + timedelta(days=11)
    data = call(PLANNING, {'monSite': site_id, 'dateLimit': f'{friday.year}-{friday.month}-{friday.day}'}, opener)
    if not truthy(pick(data, 'SUCCESS')):
        return None
    return pick(data, 'DATA')


def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(str(value or ''))).strip()


def parse_day(value):
    """Accepte ISO, jj/mm/aaaa, jj-mm-aaaa et le format anglais de ColdFusion ('October, 13 2026')."""
    text = str(value or '')
    if m := re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', text):
        y, mo, d = map(int, m.groups())
    elif m := re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', text):
        d, mo, y = map(int, m.groups())
    elif m := re.search(r'([A-Za-z]+),? (\d{1,2}),? (\d{4})', text):
        mo, d, y = MONTHS.get(m.group(1).lower()), int(m.group(2)), int(m.group(3))
    else:
        return None
    try:
        return date(y, mo, d)
    except (TypeError, ValueError):
        return None


def dishes(recipes):
    if isinstance(recipes, dict):
        recipes = list(recipes.values())
    found = []
    for recipe in recipes if isinstance(recipes, list) else []:
        label = clean(pick(recipe, 'RECETTELIB'))
        if label.count('"') == 1:  # guillemet isolé laissé dans la saisie du menu
            label = label.strip('"').strip()
        if label:
            found.append({'type': clean(pick(recipe, 'TYPONAME')), 'label': label})
    return found


def collect(*plannings):
    """Fusionne les plannings en {jour: {restaurant: [plats]}} sans doublon, ordre conservé."""
    merged = {}
    for planning in plannings:
        if isinstance(planning, dict):
            planning = list(planning.values())
        for restaurant in planning if isinstance(planning, list) else []:
            if not isinstance(restaurant, dict):
                continue
            name = clean(pick(restaurant, 'ZSLIBELLE')) or 'Restaurant'
            programme = pick(restaurant, 'PROGRAMME')
            if isinstance(programme, list):
                pairs = [(pick(p, 'DATE'), pick(p, 'RECETTE')) for p in programme]
            else:
                pairs = list(restaurant.items())
            for key, recipes in pairs:
                day = parse_day(key)
                if day is None:
                    continue
                target = merged.setdefault(day, {}).setdefault(name, [])
                for dish in dishes(recipes):
                    if dish not in target:
                        target.append(dish)
    return merged


def build(merged, today, now):
    days = [{'date': day.isoformat(),
             'restaurants': [{'name': name, 'items': items} for name, items in sorted(by_name.items()) if items]}
            for day, by_name in sorted(merged.items()) if day >= today - timedelta(days=1)]
    days = [d for d in days if d['restaurants']]
    if not days:
        raise MenuError('Aucun menu dans la réponse de myMRS : publication bloquée')
    return {'days': days, 'updated': now.strftime('%d/%m/%Y à %H:%M'), 'updatedAt': now.isoformat(timespec='minutes')}


def render(data):
    # Le contenu distant n'est jamais interprété comme du HTML ou du JavaScript.
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return (ROOT / 'template_menu.html').read_text(encoding='utf-8').replace('__MENU_DATA__', payload)


def shape(value, depth=0):
    """Squelette d'une réponse (clés, types, longueurs) pour vérifier sa forme sans rien deviner."""
    if isinstance(value, dict):
        return '{…}' if depth >= 5 else {str(k): shape(v, depth + 1) for k, v in list(value.items())[:12]}
    if isinstance(value, list):
        return [f'{len(value)} éléments'] + ([shape(value[0], depth + 1)] if value else [])
    if isinstance(value, str):
        return 'texte:' + value[:40]
    return f'{type(value).__name__}:{str(value)[:20]}'


def keys_only(value):
    return sorted(map(str, value)) if isinstance(value, dict) else type(value).__name__


def diagnostic(identity, today, opener=urlopen):
    """Affiche la forme des réponses. Les données personnelles (MESINFOS, jeton) n'y figurent jamais :
    seulement leurs noms de champs."""
    data = call(LOGIN, {**identity, 'device': DEVICE}, opener)
    infos = pick(data, 'MESINFOS')
    sites = pick(infos, 'MESSITE') or []
    report = {'connexion': {'clés': keys_only(data), 'SUCCESS': pick(data, 'SUCCESS')},
              'MESINFOS': keys_only(infos),
              'MESSITE[0]': keys_only(sites[0]) if sites else 'aucun site',
              'MONPLANNING': shape(pick(data, 'MONPLANNING'))}
    site_id = pick(sites[0], 'SITEID') if sites else None
    if site_id is not None:
        friday = today - timedelta(days=today.weekday()) + timedelta(days=11)
        extra = call(PLANNING, {'monSite': site_id, 'dateLimit': f'{friday.year}-{friday.month}-{friday.day}'}, opener)
        report['semaine suivante'] = {'clés': keys_only(extra), 'SUCCESS': pick(extra, 'SUCCESS'),
                                      'DATA': shape(pick(extra, 'DATA'))}
    print(json.dumps(report, ensure_ascii=False, indent=1))


def has_current_menu(path, today):
    """Vrai si menu.json contient au moins un jour à partir d'aujourd'hui."""
    try:
        days = json.loads(path.read_text(encoding='utf-8'))['days']
        return any(parse_day(d.get('date')) >= today for d in days)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'menu.html')
    parser.add_argument('--diagnostic', action='store_true', help='affiche la forme des réponses, ne publie rien')
    parser.add_argument('--only-if-missing', action='store_true',
                        help="ne contacte myMRS que si menu.json ne contient aucun menu pour aujourd'hui ou plus tard")
    parser.add_argument('--render-only', action='store_true',
                        help="reconstruit la page depuis menu.json sans interroger myMRS (nouvelle mise en page, menu inchangé)")
    args = parser.parse_args()
    if args.render_only:
        try:
            data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            sys.exit('Erreur : menu.json introuvable ou illisible.')
        atomic_write(args.output, render(data).encode('utf-8'))
        print(f"Page reconstruite depuis menu.json (menu du {data.get('updated', '?')}).")
        return
    if args.only_if_missing and has_current_menu(DATA_FILE, datetime.now(PARIS).date()):
        print("Menu déjà à jour pour aujourd'hui : myMRS n'est pas interrogé.")
        return
    try:
        identities = identities_from_env()
    except MenuError as error:
        sys.exit(f'Erreur : {error}')
    if not identities:
        sys.exit('Erreur : définir MYMRS_LOGIN + MYMRS_PASSWORD (ou MYMRS_PASSWORD_HEX), ou MYMRS_TOKEN.')
    now = datetime.now(PARIS)
    if args.diagnostic:
        try:
            diagnostic(identities[0], now.date())
        except MenuError as error:
            sys.exit(f'Erreur : {error}')
        return
    try:
        site_id = planning = None
        for position, identity in enumerate(identities):
            try:
                site_id, planning = open_session(identity)
                break
            except MenuError as error:
                if position == len(identities) - 1:
                    raise
                print(f'Avertissement : {error} ; essai avec l\'accès suivant', file=sys.stderr)
        extra = None
        if site_id is not None:
            try:
                extra = next_week_planning(site_id, now.date())
            except MenuError as error:  # la semaine suivante est un bonus, pas une condition
                print(f'Avertissement : semaine suivante indisponible ({error})', file=sys.stderr)
        data = build(collect(planning, extra), now.date(), now)
    except MenuError as error:
        sys.exit(f'Erreur : {error}')
    atomic_write(DATA_FILE, (json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    atomic_write(args.output, render(data).encode('utf-8'))
    print(json.dumps({'jours': len(data['days']), 'restaurants': sorted({r['name'] for d in data['days'] for r in d['restaurants']})},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
