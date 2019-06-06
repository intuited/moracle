from unittest import TestCase, main
from os import path

install_dir = path.dirname(path.abspath(__file__))

class Test(TestCase):
    def setUp(self):
        from mtgcardtext import load_db
        self.db = load_db(install_dir + "/AllCards.json")

    def test_format_oneline(self):
        """Test formatting for one-line output.
        TODO:
            - add something with Phyrexian cost
            - something with double-digit colourless
            - test incorrect string
            - test case insensitivity
        """
        from mtgcardtext import format_oneline

        test_strings = {
            'Polluted Delta'          : "Polluted Delta: L {T}, Pay 1 life, Sacrifice Polluted Delta: Search your library for an Island or Swamp card, put it onto the battlefield,",
            'Merfolk Trickster'       : "Merfolk Trickster: [UU] C 2/2 Flash\tWhen Merfolk Trickster enters the battlefield, tap target creature an opponent controls. It loses all abilities un",
            'Oath of Teferi'          : "Oath of Teferi: [3WU] E When Oath of Teferi enters the battlefield, exile another target permanent you control. Return it to the battlefield und",
            'Counterspell'            : "Counterspell: [UU] I Counter target spell.",
            'Wrath of God'            : "Wrath of God: [2WW] S Destroy all creatures. They can't be regenerated.",
            'Helm of the Host'        : "Helm of the Host: [4] A At the beginning of combat on your turn, create a token that's a copy of equipped creature, except the token isn't legen",
            'Steel of the Godhead'    : "Steel of the Godhead: [2{W/U}] E Enchant creature\tAs long as enchanted creature is white, it gets +1/+1 and has lifelink. (Damage dealt by the creature a",
            'Ephara, God of the Polis': "Ephara, God of the Polis: [2WU] EC 6/5 Indestructible\tAs long as your devotion to white and blue is less than seven, Ephara isn't a creature.\tAt the beginning ",
            'Teferi, Time Raveler'    : "Teferi, Time Raveler: [1WU] P L:4 Each opponent can cast spells only any time they could cast a sorcery.\t+1: Until your next turn, you may cast sorcery sp"}

        for name in test_strings.keys():
            ##!! print(format_oneline(self.db[name]))
            self.assertEqual(test_strings[name], format_oneline(self.db[name]))

if __name__ == '__main__':
    main()
