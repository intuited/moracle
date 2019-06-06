## mtgcardtext ##

CLI to format Magic: the Gathering card text.  Probably not something you need unless you are the sort of person who enjoys building deck lists in `vim` or another text editor.  Particularly useful for EDH decks.

Primary usage is to spit out one-line summaries of card text:

    ~/src $ PYTHONPATH=~/src python3 mtgcardtext Counterspell
    Counterspell: [UU] I Counter target spell.

By default it truncates the text at a maximum of 120 characters.  This can be changed.

    ~/src $ PYTHONPATH=~/src python3 mtgcardtext -t80 'Polluted Delta'
    Polluted Delta: L {T}, Pay 1 life, Sacrifice Polluted Delta: Search your library

    ~/src $ PYTHONPATH=~/src python3 mtgcardtext -t400 'teferi, time raveler'
    Teferi, Time Raveler: [1WU] P L:4 Each opponent can cast spells only any time they could cast a sorcery.	+1: Until your next turn, you may cast sorcery spells as though they had flash.	−3: Return up to one target artifact, creature, or enchantment to its owner's hand.	Draw a card.

Newlines in the rules text are tranformed into tab characters.

Passing the `-f` command line option will cause full-form text to be output instead of single-line format.

    ~/src $ PYTHONPATH=~/src python3 mtgcardtext -f 'ePhaRa, GoD oF thE pOliS'
    Ephara, God of the Polis: {2}{W}{U}
    Legendary Enchantment Creature — God
    Indestructible
    As long as your devotion to white and blue is less than seven, Ephara isn't a creature.
    At the beginning of each upkeep, if you had another creature enter the battlefield under your control last turn, draw a card.
    6/5

Card names must be given in full; no particular case is required.

The `-t` option does not currently work in combination with `-f`.

If no card names are passed on the command line, card names will be read from standard input, one line at a time.

### Initializing/Updating the DB ###

The card database from [mtgjson](https://mtgjson.com/#our-mission) is used.

It can be initialized or updated by supplying a database file.

    ~/tmp $ curl -O 'https://mtgjson.com/json/AllCards.json.zip'
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100 21.0M  100 21.0M    0     0  1503k      0  0:00:14  0:00:14 --:--:-- 2352k
    ~/tmp $ PYTHONPATH=~/src python3 -m mtgcardtext -u AllCards.json.zip
    Internal database updated from file "AllCards.json.zip".

You'll need to do this before you can use `mtgcardtext`.
