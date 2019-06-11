import moracle
from unittest import TestCase, main
from os import path

install_dir = path.dirname(path.abspath(__file__))

class TestFormat(TestCase):
    def setUp(self):
        from moracle import load_db
        self.db = load_db(install_dir + "/AllCards.json")

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

if __name__ == '__main__':
    main()
