## moracle ##

CLI to format Magic: the Gathering card text, otherwise known as Oracle data.  Probably not something you need unless you are the sort of person who enjoys building deck lists in `vim` or another text editor.  Particularly useful for EDH decks.

NOTE: examples assume that you've cloned the repo into ~/src, for example with

    $ cd ~/src
    $ git clone https://github.com/intuited/moracle.git

Running the utility will get less complicated when I have some time to properly package it and put it up on pypi.

For now you'll have to run the module with `-m moracle` and add the directory where you cloned the repo to your `PYTHONPATH`.

Before using it you'll have to [update the card database](#Updating-the-DB).

### One-line format ###

`moracle`'s primary usage is to spit out one-line summaries of card text:

    $ PYTHONPATH=~/src python3 -m moracle Counterspell
    Counterspell: [UU] I Counter target spell.

`-w` sets a maximum total length for the one-line output.

    $ PYTHONPATH=~/src python3 -m moracle -t80 'teferi, time raveler'
    Teferi, Time Raveler: [1WU] P L:4 Each opponent can cast spells only any time th

Newlines in the rules text are tranformed into tab characters.

Output should be mostly self-explanatory.

    NAME [COST] TYPE [P/T | L] RULES

`COST` is the full casting cost

`TYPE` consists of one or more single-letter abbreviations for Creature, Enchantment, Sorcery, Instant, Artifact, Planeswalker, or Land

`P/T` is a creature's Power/Toughness

`L` is a planeswalker's Loyalty

`RULES` is the rules text

### Full format ###

Passing the `-f` command line option will cause full-form text to be output instead of single-line format.  Newlines in the rules text are retained, and the overall layout is similar to that of an actual card.

    $ PYTHONPATH=~/src python3 -m moracle -f 'ePhaRa, GoD oF thE pOliS'
    Ephara, God of the Polis: {2}{W}{U}
    Legendary Enchantment Creature — God
    Indestructible
    As long as your devotion to white and blue is less than seven, Ephara isn't a creature.
    At the beginning of each upkeep, if you had another creature enter the battlefield under your control last turn, draw a card.
    6/5

Card names must be given in full; no particular case is required.

Passing `-w` in combination with `-f` will cause the rules text to be wrapped at that width.
    
    $ PYTHONPATH=~/src python3 -m moracle -w80 -f 'Teferi, Temporal Archmage'
    Teferi, Temporal Archmage: {4}{U}{U}
    Legendary Planeswalker — Teferi
    +1: Look at the top two cards of your library. Put one of them into your hand
    and the other on the bottom of your library.
    −1: Untap up to four target permanents.
    −10: You get an emblem with "You may activate loyalty abilities of planeswalkers
    you control on any player's turn any time you could cast an instant."
    Teferi, Temporal Archmage can be your commander.
    Loyalty: 5

### Card names from stdin ###

If no card names are passed on the command line, card names will be read from standard input, one line at a time.

### Updating the DB ###

The card database from [mtgjson](https://mtgjson.com/#our-mission) is used.

It will need to be initialized before use and also updated when information from new sets is added.

The easiest way to do this is by simply running

    $ PYTHONPATH=~/src python3 -m moracle -u
    Updating internal database from "https://mtgjson.com/json/AllCards.json.zip"...
    21.1MB [00:30, 724kB/s]
    Update successful.

`moracle`'s db can also be initialized or updated by supplying a database file, either in json format or as a zip file containing the file 'AllCards.json'.

    ~/tmp $ curl -O 'https://mtgjson.com/json/AllCards.json.zip'
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100 21.0M  100 21.0M    0     0  1503k      0  0:00:14  0:00:14 --:--:-- 2352k
    ~/tmp $ PYTHONPATH=~/src python3 -m moracle -u AllCards.json.zip
    Internal database updated from file "AllCards.json.zip".

You'll need to do this before you can use `moracle`.
