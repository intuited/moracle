import moracle
from unittest import TestCase, main
from os import path

install_dir = path.dirname(path.abspath(__file__))

test_db = moracle.load_db(install_dir + "/AllCards.json")

class TestFormat(TestCase):
    def setUp(self):
        self.db = test_db

    def test_format_oneline(self):
        """Test formatting for one-line output.
        TODO:
            - add something with Phyrexian cost
            - something with double-digit colourless
            - test incorrect string
            - test case insensitivity
        """
        from moracle import format_oneline

        test_data = [
            {   'name': 'Polluted Delta',
                'width': 120,
                'result': "Polluted Delta: L {T}, Pay 1 life, Sacrifice Polluted Delta: Search your library for an Island or Swamp card, put it ont"},
            {   'name': 'Merfolk Trickster',
                'width': 120,
                'result': "Merfolk Trickster: [UU] C 2/2 Flash\tWhen Merfolk Trickster enters the battlefield, tap target creature an opponent contr"},
            {   'name': 'Oath of Teferi',
                'width': 120,
                'result': "Oath of Teferi: [3WU] E When Oath of Teferi enters the battlefield, exile another target permanent you control. Return i"},
            {   'name': 'Counterspell',
                'width': None,
                'result': "Counterspell: [UU] I Counter target spell."},
            {   'name': 'Wrath of God',
                'width': 0,
                'result': "Wrath of God: [2WW] S Destroy all creatures. They can't be regenerated."},
            {   'name': 'Helm of the Host',
                'width': 120,
                'result': "Helm of the Host: [4] A At the beginning of combat on your turn, create a token that's a copy of equipped creature, exce"},
            {   'name': 'Steel of the Godhead',
                'width': 120,
                'result': "Steel of the Godhead: [2{W/U}] E Enchant creature\tAs long as enchanted creature is white, it gets +1/+1 and has lifelink"},
            {   'name': 'Ephara, God of the Polis',
                'width': 120,
                'result':"Ephara, God of the Polis: [2WU] EC 6/5 Indestructible\tAs long as your devotion to white and blue is less than seven, Eph"},
            {   'name': 'Teferi, Time Raveler',
                'width': 120,
                'result': "Teferi, Time Raveler: [1WU] P L:4 Each opponent can cast spells only any time they could cast a sorcery.\t+1: Until your "},
            {   'name': 'postmortem LUNGE',
                'width': 120,
                'result': "Postmortem Lunge: [X{B/P}] S ({B/P} can be paid with either {B} or 2 life.)\tReturn target creature card with converted m"},
            {   'name': 'blinkmoth infusion',
                'width': None,
                'result': "Blinkmoth Infusion: [12UU] I Affinity for artifacts (This spell costs {1} less to cast for each artifact you control.)\tUntap all artifacts."}]

        for card in test_data:
            if card['width'] is None:
                result = format_oneline(self.db[card['name'].lower()])
            else:
                result = format_oneline(self.db[card['name'].lower()], card['width'])
            self.assertEqual(result, card['result']) 

    def test_format_full(self):
        """Test formatting of full format output."""
        from textwrap import dedent
        from moracle import format_full

        test_data = [
            {   'name': 'Teferi, Time Raveler',
                'width': 40,
                'result': dedent("""\
                    Teferi, Time Raveler           {1}{W}{U}
                        Legendary Planeswalker — Teferi
                    Each opponent can cast spells only any
                    time they could cast a sorcery.
                    +1: Until your next turn, you may cast
                    sorcery spells as though they had flash.
                    −3: Return up to one target artifact,
                    creature, or enchantment to its owner's
                    hand. Draw a card.
                                                           4\n""")
            }, {'name': 'postmortem lunge',
                'width': None,
                'result': dedent("""\
                    Postmortem Lunge: {X}{B/P}
                    Sorcery
                    ({B/P} can be paid with either {B} or 2 life.)
                    Return target creature card with converted mana cost X from your graveyard to the battlefield. It gains haste. Exile it at the beginning of the next end step.\n""")
            }, {'name': 'aToGaToG',
                'width': 60,
                'result': dedent("""\
                    Atogatog                                     {W}{U}{B}{R}{G}
                                     Legendary Creature — Atog
                    Sacrifice an Atog creature: Atogatog gets +X/+X until end of
                    turn, where X is the sacrificed creature's power.
                                                                             5/5\n""")
            }]
        for card in test_data:
            if card['width']:
                result = format_full(self.db[card['name'].lower()], card['width'])
            else:
                result = format_full(self.db[card['name'].lower()])
            self.assertEqual(result, card['result'])

class TestDBLoad(TestCase):
    def setUp(self):
        self.json = '[{"1": "one"}, {"2": "two"}, {"3": "three"}]'
        self.correct_db = [{'1': "one"}, {'2': "two"}, {'3': "three"}]

    def test_json_file(self):
        from tempfile import mkstemp
        import os

        fd, filename = mkstemp()
        try:
            with os.fdopen(fd, mode='w') as jsonfile:
                jsonfile.write(self.json)
            db = moracle.load_db(filename)
            self.assertEqual(db, self.correct_db)
        finally:
            os.remove(filename)

    def test_zip_file(self):
        from tempfile import mkstemp
        from zipfile import ZipFile
        import os

        fd, filename = mkstemp(suffix='.zip')
        try:
            with ZipFile(filename, mode='w') as z:
                z.writestr(moracle.DB_ZIP_CONTENT, self.json)
            db = moracle.load_db(filename)
            self.assertEqual(db, self.correct_db)
        finally:
            os.remove(filename)

    def test_json_url(self):
        import responses
        import requests

        with responses.RequestsMock() as res:
            res.add(responses.GET, 'https://mtgjson.com/json/AllCards.json', 
                    body=self.json, status=200, content_type="application/json")
            db = moracle.load_db('https://mtgjson.com/json/AllCards.json')
            self.assertEqual(db, self.correct_db)

    def test_zip_url(self):
        import responses
        import requests
        from io import BytesIO
        from zipfile import ZipFile

        buff = BytesIO()
        with ZipFile(buff, 'w') as z:
            z.writestr(moracle.DB_ZIP_CONTENT, self.json)

        with responses.RequestsMock() as res:
            res.add(responses.GET, 'https://mtgjson.com/json/AllCards.json.zip',
                    body=buff.getbuffer(), status=200, content_type="application/zip")
            db = moracle.load_db('https://mtgjson.com/json/AllCards.json.zip')
            self.assertEqual(db, self.correct_db)

class TestLookup(TestCase):
    def setUp(self):
        self.db = test_db

    def test_lookup_full_nocaps(self):
        """Test lookup of full card name in the database."""
        self.assertIs(moracle.lookup(self.db, 'swamp'), self.db['swamp'])

    def test_lookup_full_normalcaps(self):
        """Test lookup of full card name in the database."""
        self.assertIs(moracle.lookup(self.db, 'Teferi, Temporal Archmage'),
                         self.db['teferi, temporal archmage'])
    def test_lookup_full_randomcaps(self):
        """Test lookup of full card name in the database."""
        self.assertIs(moracle.lookup(self.db, 'aToGaTOG'),
                         self.db['atogatog'],
                         'full')

    def test_lookup_start(self):
        teferis = ["teferi, hero of dominaria",
                   "teferi, mage of zhalfir",
                   "teferi's care",
                   "teferi's curse",
                   "teferi's drake",
                   "teferi's honor guard",
                   "teferi's imp",
                   "teferi's isle",
                   "teferi's moat",
                   "teferi's protection",
                   "teferi's puzzle box",
                   "teferi's realm",
                   "teferi's response",
                   "teferi's sentinel",
                   "teferi's time twist",
                   "teferi's veil",
                   "teferi, temporal archmage",
                   "teferi, timebender",
                   "teferi, time raveler"]
        self.assertEqual(set(moracle.lookup(self.db, 'Teferi', 'start').keys()),
                         set(teferis))

    def test_lookup_in(self):
        intos = ["cast into darkness",
                 "descent into madness",
                 "dismiss into dream",
                 "exile into darkness",
                 "fade into antiquity",
                 "fold into aether",
                 "into the core",
                 "into the earthen maw",
                 "into the fray",
                 "into the maw of hell",
                 "into the north",
                 "into the roil",
                 "into the void",
                 "into the wilds",
                 "into thin air",
                 "mask of intolerance",
                 "open into wonder",
                 "plunge into darkness",
                 "press into service",
                 "sink into takenuma",
                 "spin into myth",
                 "take into custody",
                 "vanish into memory",
                 "write into being"]

        self.assertEqual(set(moracle.lookup(self.db, 'INTO', 'in').keys()),
                         set(intos))

class TestSplitString(TestCase):
    def test_empty_string(self):
        self.assertEqual(moracle.split_string(''), [])

    def test_whitespace(self):
        self.assertEqual(moracle.split_string(' '), [])

    def test_one_word(self):
        self.assertEqual(moracle.split_string('word'), [('word', 0, 3)])

    def test_word_with_leading_whitespace(self):
        self.assertEqual(moracle.split_string(' word'), [('word', 1, 4)])

    def test_word_with_trailing_whitespace(self):
        self.assertEqual(moracle.split_string('word '), [('word', 0, 3)])

    def test_word_within_whitespace(self):
        self.assertEqual(moracle.split_string(' word '), [('word', 1, 4)])

    def test_word_within_long_whitespace(self):
        self.assertEqual(moracle.split_string('  word   '), [('word', 2, 5)])

    def test_two_words(self):
        self.assertEqual(moracle.split_string('word1 word2'),
                         [('word1', 0, 4), ('word2', 6, 10)])

    def test_two_words_within_long_whitespace(self):
        self.assertEqual(moracle.split_string('   word1  word2  '),
                         [('word1', 3, 7), ('word2', 10, 14)])

    def test_three_words(self):
        self.assertEqual(moracle.split_string('word1 word2 word3'),
                         [('word1', 0, 4), ('word2', 6, 10), ('word3', 12, 16)])

class TestCursorWord(TestCase):
    def setUp(self):
        self.two_words = [('word1', 1, 6), ('word2', 9, 14)]

    def test_no_words(self):
        self.assertEqual(moracle.cursor_word([], 0), -1)

    def test_no_words_nonzero_pos(self):
        self.assertEqual(moracle.cursor_word([], 3), -1)

    def test_one_word_at_zero_with_zero_pos(self):
        self.assertEqual(moracle.cursor_word([('word', 0, 4)], 0), 0)

    def test_one_word_at_zero_with_nonzero_pos(self):
        self.assertEqual(moracle.cursor_word([('word', 0, 4)], 2), 0)

    def test_one_word_at_nonzero_with_zero_pos(self):
        self.assertEqual(moracle.cursor_word([('word', 3, 7)], 0), -1)

    def test_one_word_at_nonzero_with_nonzero_miss_pos(self):
        self.assertEqual(moracle.cursor_word([('word', 3, 7)], 2), -1)

    def test_one_word_at_nonzero_with_nonzero_hit_pos(self):
        self.assertEqual(moracle.cursor_word([('word', 3, 7)], 3), 0)

    def test_one_word_at_zero_with_pos_at_end_of_word(self):
        self.assertEqual(moracle.cursor_word([('word', 0, 4)], 4), 0)

    def test_one_word_at_zero_with_pos_after_word(self):
        self.assertEqual(moracle.cursor_word([('word', 0, 4)], 5), 0)

    def test_two_words_with_pos_before_first_word(self):
        self.assertEqual(moracle.cursor_word(self.two_words, 0), -1)

    def test_two_words_with_pos_in_first_word(self):
        self.assertEqual(moracle.cursor_word(self.two_words, 2), 0)

    def test_two_words_with_pos_after_first_word(self):
        self.assertEqual(moracle.cursor_word(self.two_words, 7), 0)

    def test_two_words_with_pos_before_second_word(self):
        self.assertEqual(moracle.cursor_word(self.two_words, 8), 0)

    def test_two_words_with_pos_in_second_word(self):
        self.assertEqual(moracle.cursor_word(self.two_words, 9), 1)

    def test_two_words_with_pos_after_second_word(self):
        self.assertEqual(moracle.cursor_word(self.two_words, 15), 1)

class TestIdentifyCardName(TestCase):
    def setUp(self):
        self.db = test_db

    def test_oneword(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'swamp', 0),
                         (0, 4, 'Swamp'))
    def test_left_of_oneword(self):
        self.assertEqual(moracle.identify_card_name(self.db, ' swamp', 0),
                         None)
    def test_right_of_oneword(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'swamp ', 5),
                         (0, 4, 'Swamp'))
    def test_middle_of_twoword(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'island sanctuary', 6),
                         (0, 15, 'Island Sanctuary'))
    def test_beginning_of_twoword(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'island sanctuary', 0),
                         (0, 15, 'Island Sanctuary'))
    def test_end_of_twoword(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'island sanctuary', 15),
                         (0, 15, 'Island Sanctuary'))
    def test_twoword_gibberish(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'island septictank', 0),
                         (0, 5, 'Island'))
    def test_second_word_of_two_word_card_where_second_word_is_also_card(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'volcanic island', 11),
                         (0, 14, 'Volcanic Island'))
    def test_first_word_gibberish_second_word_card(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'voltronic island', 1),
                         None)
    def test_on_second_of_four_words(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'jace, the mind sculptor', 8),
                         (0, 22, 'Jace, the Mind Sculptor'))
    def test_card_name_amongst_other_ones(self):
        self.assertEqual(moracle.identify_card_name(self.db, 'island, swamp, plains', 10),
                         (8, 12, 'Swamp'))
    def test_lots_of_parentheses_and_shit(self):
        self.assertEqual(moracle.identify_card_name(self.db, "most expensive card: (volcanic island)", 30),
                         (22, 36, 'Volcanic Island'))
    def test_incomplete_card_name(self):
        self.assertEqual(moracle.identify_card_name(self.db, "I am typing the card 'Volcanic Isla", 24),
                         (22, 34, 'Volcanic Island'))
    def test_incomplete_ambiguous_card_name(self):
        self.assertEqual(set(moracle.identify_card_name(self.db, "I am typing the card 'Volcanic R", 24).keys()),
                         {'volcanic rambler', 'volcanic rush'})
    def test_incomplete_ambiguous_card_name_cursor_at_end(self):
        self.assertEqual(set(moracle.identify_card_name(self.db, "I am typing the card 'Volcanic R", 32).keys()),
                         {'volcanic rambler', 'volcanic rush'})

if __name__ == '__main__':
    main()
