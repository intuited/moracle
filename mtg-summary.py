from json import load

db_file = open('./AllCards.json')
jsdb = load(db_file)
db_file.close()

# operation modes
#   help: spits out syntax info
#   transform: reads card names, one per line, and outputs one-line formatted card info for each
#   args: outputs info for card names passed as command line arguments.
#     -f: output full info for each card rather than the default one-line format
#   update: gets a new copy of the db and saves it wherever it saves the db.

# options
# -i: names read from stdin or args are not case sensitive
# -f: print full info for card names passed in args mode
# -tX: text field cropped at a maximum of X characters

# how do I actually want to do this
correct_strings = {
  'Polluted Delta'          : '',
  'Merfolk Trickster'       : '',
  'Oath of Teferi'          : '',
  'Counterspell'            : '',
  'Wrath of God'            : '',
  'Helm of the Host'        : '',
  'Steel of the Godhead'    : '',
  'Ephara, God of the Polis': '',
# add something with Phyrexian cost
# something with double-digit colourless
# test incorrect string
# test case insensitivity
  'Teferi, Time Raveler'    : ''}

# Transform card type info from the full string to abbreviations.
def abbrev_cardtype(card_type):
  abbrevs = {
    'Creature'     : 'C',
    'Enchantment'  : 'E',
    'Sorcery'      : 'S',
    'Instant'      : 'I',
    'Artifact'     : 'A',
    'Planeswalker' : 'P',
    'Land'         : 'L'}
  return ''.join(abbrevs[word] for word in card_type.split(' ') if word in abbrevs.keys())

# Removes braces around simple mana cost components
def abbrev_manacost(cost):
  from re import sub
  return sub(r'\{([0-9]+|[A-Z])\}', r'\1', cost)
  
# Format the card data for a 1-line presentation.
# The 'text' field is cropped at a maximum of `text_crop` characters.
def format_oneline(card, text_crop=120):
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

for card in correct_strings.keys():
  print(format_oneline(jsdb[card]))
