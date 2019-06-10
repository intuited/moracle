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

        test_strings = {
            'Polluted Delta'          : "Polluted Delta: L {T}, Pay 1 life, Sacrifice Polluted Delta: Search your library for an Island or Swamp card, put it ont",
            'Merfolk Trickster'       : "Merfolk Trickster: [UU] C 2/2 Flash\tWhen Merfolk Trickster enters the battlefield, tap target creature an opponent contr",
            'Oath of Teferi'          : "Oath of Teferi: [3WU] E When Oath of Teferi enters the battlefield, exile another target permanent you control. Return i",
            'Counterspell'            : "Counterspell: [UU] I Counter target spell.",
            'Wrath of God'            : "Wrath of God: [2WW] S Destroy all creatures. They can't be regenerated.",
            'Helm of the Host'        : "Helm of the Host: [4] A At the beginning of combat on your turn, create a token that's a copy of equipped creature, exce",
            'Steel of the Godhead'    : "Steel of the Godhead: [2{W/U}] E Enchant creature\tAs long as enchanted creature is white, it gets +1/+1 and has lifelink",
            'Ephara, God of the Polis': "Ephara, God of the Polis: [2WU] EC 6/5 Indestructible\tAs long as your devotion to white and blue is less than seven, Eph",
            'Teferi, Time Raveler'    : "Teferi, Time Raveler: [1WU] P L:4 Each opponent can cast spells only any time they could cast a sorcery.\t+1: Until your "}

        for name in test_strings.keys():
            ##!! print(format_oneline(self.db[name]))
            self.assertEqual(test_strings[name], format_oneline(self.db[name]))

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
