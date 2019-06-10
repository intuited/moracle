"""Format info from the mtgjson repo for human use.  Output format:

NAME [COST] TYPE [P/T | L] RULES

COST is the full casting cost
TYPE consists of one or more single-letter abbreviations for
  Creature, Enchantment, Sorcery, Instant, Artifact,
  Planeswalker, or Land
P/T is a creature's Power/Toughness
L is a planeswalker's Loyalty
RULES is the rules text
"""
from os import path

INSTALL_DIR = path.dirname(path.abspath(__file__))
DEFAULT_DB_LOCATION = INSTALL_DIR + "/AllCards.json"
DB_ZIP_CONTENT = 'AllCards.json'
DEFAULT_UPDATE_URL = 'https://mtgjson.com/json/AllCards.json.zip'

def load_db(source=DEFAULT_DB_LOCATION, progress=False):
    """Load the db from a local file.

    Can load from a zip file (for updates) or unzipped .json file.

    When reading from a zip file, the db must be contained in a file
    with name matching DB_ZIP_CONTENT.

    If `progress` is True and `source` is a URL,
    download progress will be displayed while loading the db.

    Returns the de-JSONed data as a heirarchy of Python objects.
    """
    import requests
    from zipfile import ZipFile
    from io import BytesIO
    import json
    from tqdm import tqdm

    if source[-4:] == '.zip':
        zipped = True
    else:
        zipped = False

    try:
        r = requests.get(source)

        it = r.iter_content()
        if progress:
            it = tqdm(it, unit_scale=True, unit_divisor=1024, unit='B')

        buf = BytesIO()
        for chunk in it:
            buf.write(chunk)

        if zipped:
            with ZipFile(buf) as z:
                return json.loads(z.read(DB_ZIP_CONTENT))
        else:
            return json.loads(r.content)

    except requests.exceptions.MissingSchema as e:
        if zipped:
            with ZipFile(source) as z:
                return json.loads(z.read(DB_ZIP_CONTENT))
        else:
            with open(source) as f:
                return json.load(f)

def abbrev_cardtype(card_type):
    """Transform card type info from the full string to abbreviations.

    Major card types are retained and transformed to single capital letters.
    This includes Creature, Enchantment, Sorcery, Instant, Artifact, Planeswalker,
    and Land.
    Other card types are ignored.
    """
    abbrevs = {
        'Creature'     : 'C',
        'Enchantment'  : 'E',
        'Sorcery'      : 'S',
        'Instant'      : 'I',
        'Artifact'     : 'A',
        'Planeswalker' : 'P',
        'Land'         : 'L'}
    return ''.join(abbrevs[word] for word in card_type.split(' ') if word in abbrevs.keys())

def abbrev_manacost(cost):
    """Remove braces around simple mana cost components.
    
    Simple components are single-character letters or numbers of any size.
    """
    from re import sub
    return sub(r'\{([0-9]+|[A-Z])\}', r'\1', cost)

def format_oneline(card, text_crop=120):
    """Format the card data for a 1-line presentation.

    The result is cropped at a maximum of `text_crop` characters.
    Newlines in the rules text are converted to tabs.
    """
    components = []

    components.append(card['name'] + ':')
    if 'manaCost' in card.keys():
        components.append('[' + abbrev_manacost(card['manaCost']) + ']')
    components.append(abbrev_cardtype(card['type']))
    if 'power' in card.keys():
        components.append(card['power'] + '/' + card['toughness'])
    if 'loyalty' in card.keys():
        components.append('L:' + card['loyalty'])

    components.append(card['text'].replace('\n', '\t'))

    return ' '.join(components)[0:text_crop]

def format_full(card, text_crop=0):
    components = []
    header = card['name']
    if 'manaCost' in card.keys():
        header += ': ' + card['manaCost']
    components.append(header)
    components.append(card['type'])
    components.append(card['text'])
    if 'power' in card.keys():
        components.append(card['power'] + '/' + card['toughness'])
    elif 'loyalty' in card.keys():
        components.append('Loyalty: ' + card['loyalty'])
    return '\n'.join(components) + '\n'

def update_db(source):
    """Update the card database from a URL or a local file.

    The provided db file can be zipped or not.
    """
    import json

    db = load_db(source, progress=True)

    lowerdb = dict((key.lower(), value) for key, value in db.items())

    with open(DEFAULT_DB_LOCATION, 'w') as out:
        json.dump(lowerdb, out)

def cli():
    from argparse import ArgumentParser, FileType
    from argparse import RawDescriptionHelpFormatter as fmt
    from fileinput import input
    from sys import stderr

    parser = ArgumentParser(description=__doc__, formatter_class=fmt)
    parser.add_argument('-u', '--update', nargs="?", dest='source',
                        const=DEFAULT_UPDATE_URL,
                        help="Import DB file UPDATE as .zip or .json")
    parser.add_argument('-f', '--full', action='store_const', const=format_full,
                        default=format_oneline, dest='formatter',
                        help="Output full card text rather than one-line info.")
    parser.add_argument('-t', '--textlength', action='store', dest='textlength',
                        type=int, default=120,
                        help="Max line length of TEXTLENGTH characters. (120)")
    parser.add_argument('cards', nargs='*', action='store',
                        help="If -u not specified and no cards given, "
                           + "cards will be read from stdin.")

    args = parser.parse_args()

    if args.source:
        stderr.write('Updating internal database from "' + args.source
                     + '"...\n')
        update_db(args.source)
        stderr.write('Update successful.\n')
    else:
        if args.cards:
            cards = args.cards
        else:
            cards = (line.strip() for line in input())

        db = load_db()

        for card in cards:
            try:
                print(args.formatter(db[card.lower()], args.textlength))
            except KeyError:
                stderr.write('Card "' + card + '" not found.\n')

if __name__ == '__main__':
    cli()
