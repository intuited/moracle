"""mtgcardtext: formats info from the mtgjasn repo for human use

operation modes
    help: spits out syntax info
    transform: reads card names, one per line, and outputs one-line formatted card info for each
    args: outputs info for card names passed as command line arguments.
      -f: output full info for each card rather than the default one-line format
    update: gets a new copy of the db and saves it wherever it saves the db.

options
    -i: names read from stdin or args are not case sensitive
    -f: print full info for card names passed in args mode
    -tX: text field cropped at a maximum of X characters (default 120)
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
