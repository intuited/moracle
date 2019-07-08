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
    """Load the db from a URL or local file.

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

def format_oneline(card, maxwidth=0):
    """Format the card data for a 1-line presentation.

    The result is cropped at a maximum of `maxwidth` characters.
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

    if 'text' in card.keys():
        components.append(card['text'].replace('\n', '\t'))

    result = ' '.join(components)

    if maxwidth:
        return result[0:maxwidth]
    else:
        return result

def format_full(card, maxwidth=0):
    """Format full card text.

    If `maxwidth` is non-zero, wrap rules at `maxwidth` characters
    and align other components as they are on cards.

    With zero `maxwidth`, left-justify everything and don't wrap.
    """
    from textwrap import wrap

    components = []

    header = card['name']
    if 'manaCost' in card.keys():
        if not maxwidth:
            header += ': '
        header += card['manaCost'].rjust(maxwidth - len(header))
    components.append(header)

    components.append(card['type'].center(maxwidth).rstrip())

    if maxwidth:
        lines = card['text'].split('\n')
        reflowed = (wrap(line, maxwidth) for line in lines)
        components += sum(reflowed, [])
    else:
        components.append(card['text'])

    if 'power' in card.keys():
        footer = card['power'] + '/' + card['toughness']
        components.append(footer.rjust(maxwidth))
    elif 'loyalty' in card.keys():
        if not maxwidth:
            footer = 'Loyalty: ' + card['loyalty']
        else:
            footer = card['loyalty']
        components.append(footer.rjust(maxwidth))

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

def lookup_full(db, string):
    try:
        return db[string.lower()]
    except KeyError:
        return None

def lookup_start(db, string):
    return dict((key, value) for key, value in db.items()
                if key.startswith(string.lower()))

def lookup_in(db, string):
    return dict((key, value) for key, value in db.items()
                if string.lower() in key)

def lookup(db, string, method='full'):
    """Return all cards matching `string` in `db`.

    The `method` determines how the search is performed.
    - 'full': Searches for a card with that exact name.  Case ignored.
    - 'start': Searches for names starting with the string.  Case ignored.
    - 'in': Searches for names with the string in it.  Case ignored.

    For the 'full' method, return value is the db Dictionary for that card,
    or None if the lookup failed.
    Otherwise, return value is a Dictionary containing the matched db dicts.
    """
    return { 'full':  lookup_full,
             'start': lookup_start,
             'in':    lookup_in     }[method](db, string)

from collections import namedtuple
Word = namedtuple('Word', ['word', 'start', 'end'])
word_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def split_string(string, chars=word_characters):
    """Splits `string` along characters not in `chars`.

    Returns a list of (word, start, end) Word tuples.
    - `word`: the word as a str
    - `start`: position in `string` of the first character of `word`
    - `end`: position in `string` of the last character of `word`
    """
    words = []
    current_word = None

    for pos in range(len(string)):
        if string[pos] in chars:
            if not current_word:
                # we found a new word!
                current_word = [None, None, None]
                current_word[0] = string[pos]
                current_word[1] = pos
                current_word[2] = pos
                words.append(current_word)
            else:
                # we're continuing to explore this word
                current_word[0] += string[pos]
                current_word[2] = pos
        else:
            current_word = None

    return [Word(*word) for word in words]

def cursor_word(words, cursor_pos):
    """
    Given a list of words from `split_string`, returns the index of the tuple
    within that list at which the cursor is located.

    If the cursor is located in whitespace or after the last word,
    returns the index of the last word before the cursor position.

    If the cursor is located in leading whitespace, or there are no words,
    returns -1.
    """
    words = [Word(*word) for word in words]

    for i, word in enumerate(words):
        if cursor_pos < word.start:
            return i - 1
        elif cursor_pos <= word.end:
            return i

    return len(words) - 1

def identify_card_name(db, line, cursor_pos, chars=word_characters):
    """Complete the card name that the cursor is located within.

    Splits `line` into words,
    and successively narrows down the search using adjacent words.

    If the cursor is located on whitespace,
    starts with the word to the left of that whitespace.
    This is for cases where the cursor is on whitespace within a card name.

    Returns the start and end positions for the section to be replaced
    as well as the card name (replacement text) as a string.

    If there is no valid replacement, returns None.
    """
    from collections import namedtuple
    MatchedCard = namedtuple('MatchedCard', ['start_pos', 'end_pos', 'name'])
    MultipleMatches = namedtuple('MultipleMatches', ['start_word', 'end_word', 'matches'])

    words = split_string(line)
    word_index = cursor_word(words, cursor_pos)

    def search_words(db, start_word, end_word, search_left=True, search_right=True):
        if start_word < 0:
            return None
        if end_word >= len(words):
            return None

        def current_replacement():
            start_pos = words[start_word].start
            end_pos = words[end_word].end
            return line[start_pos:end_pos+1]

        matches = lookup_in(db, current_replacement())

        if not matches:
            return None

        if search_left:
            result = search_words(matches, start_word - 1, end_word, search_right=False)
            if type(result) == MatchedCard:
                return result
            if type(result) == MultipleMatches:
                start_word, end_word, matches = result

        if search_right:
            result = search_words(matches, start_word, end_word + 1, search_left=False)
            if type(result) == MatchedCard:
                return result
            if type(result) == MultipleMatches:
                start_word, end_word, matches = result

        # check if the replacement zone fully matches a card name
        full_match = lookup_full(db, current_replacement())
        if full_match:
            return MatchedCard(words[start_word].start,
                               words[end_word].end,
                               full_match['name'])

        if len(matches) == 1:
            return MatchedCard(words[start_word].start,
                               words[end_word].end,
                               list(matches.values())[0]['name'])

        return MultipleMatches(start_word, end_word, matches)

    result = search_words(db, word_index, word_index)
    if type(result) == MultipleMatches:
        return result.matches
    return result

##~~  def identify_card_candidates(db, line, cursor_pos, ifs=' '):
##~~      """Provide a list of card names which match an incomplete card fragment.
##~~  
##~~      The cursor can be anywhere within the card fragment in the given line.
##~~  
##~~      Uses the same search procedure as `identify_card_name`.
##~~  
##~~      If addition of further words to the card name fragment
##~~      yields no results, searching terminates in that direction.
##~~  
##~~      Returns the start and end positions for the section to be replaced
##~~      as well as a list of possible card names to replace that section.
##~~      """

def cli():
    from argparse import ArgumentParser, FileType
    from argparse import RawDescriptionHelpFormatter as fmt
    from fileinput import input
    from sys import stderr
    import sys

    parser = ArgumentParser(description=__doc__, formatter_class=fmt)
    parser.add_argument('-u', '--update', nargs="?", dest='source',
                        const=DEFAULT_UPDATE_URL,
                        help="Import DB file UPDATE as .zip or .json")
    parser.add_argument('-f', '--full', action='store_const', const=format_full,
                        default=format_oneline, dest='formatter',
                        help="Output full card text rather than one-line info.")
    parser.add_argument('-w', '--maxwidth', action='store', dest='maxwidth',
                        type=int, default=0,
                        help="Crop one-line and wrap full format at MAXWIDTH " +
                             "characters.")
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

        try:
            db = load_db()
        except FileNotFoundError:
            stderr.write('Card database not present.\n')
            stderr.write('Run `moracle -u` to download the database.\n')
            sys.exit(1)

        for card in cards:
            try:
                print(args.formatter(lookup(db, card), args.maxwidth))
            except KeyError:
                stderr.write('Card "' + card + '" not found.\n')

if __name__ == '__main__':
    cli()
