"""mtgcardtext: formats info from the mtgjasn repo for human use

operation modes
    args: outputs info for card names passed as command line arguments.

options
    -u: update the stored card DB
    -f: print full card info rather than one-line summaries
    -tX: text field cropped at a maximum of X characters (default 120)
    -: reads card names from stdin and outputs one-line formatted card info for each
"""

DEFAULT_DB_LOCATION = "./AllCards.json"

def load_db(db_path=DEFAULT_DB_LOCATION):
    from json import load
    with open(db_path) as db_file:
        return load(db_file)

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

    The 'text' field is cropped at a maximum of `text_crop` characters.
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

    components.append(card['text'][0:text_crop].replace('\n', '\t'))

    return ' '.join(components)

def format_full(card, text_crop=0):
    raise NotImplementedError("Full formatting not yet implemented.")

def update_db():
    """Update the card database from mtgjson."""
    raise NotImplementedError("Update functionality not yet implemented")

def cli():
    from argparse import ArgumentParser
    from fileinput import input

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--update', action='store_true', dest='update')
    parser.add_argument('-f', '--full', action='store_const', const=format_full,
                        default=format_oneline, dest='formatter')
    parser.add_argument('-t', '--textlength', action='store', dest='textlength',
                        type=int, default=120)
    parser.add_argument('cards', nargs='*', action='store')

    args = parser.parse_args()

    if args.update:
        update_db()
    else:
        if args.cards:
            cards = args.cards
        else:
            cards = (line.strip() for line in input())

        db = load_db()

        for card in cards:
            print(args.formatter(db[card], args.textlength))

if __name__ == '__main__':
    cli()
