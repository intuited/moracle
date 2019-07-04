"""Search `db` for cards that match `conditions`.

Matching cards are returned as a list of dictionaries.

`conditions` is a list of dictionaries.
Each dictionary in `conditions` has the following entries:
    - operator: AND, OR, or NOT

>>> db = moracle.load_db()

Find the card "Swamp":
>>> search.search({'field': 'name', 'method': IS, 'value': 'swamp'})(db).keys()
['swamp']

Land that has "any color" in the text:
>>> search.And( {'value': 'Land',
...              'method': IN,
...              'field': 'type'},
...             {'value': 'any color',
...              'method': IN,
...              'field': 'text'} )(db)

Cards with text containing 'move' and 'counter':
>>> search.And( {'value': 'move',    'method': IN, 'field': 'text'},
...             {'value': 'counter', 'method': IN, 'field': 'text'})(db)

Cards with five-colour colour identity:
>>> search.And( Or( {'value': '{R}', 'method': IN, 'field': 'manaCost'},
...                 {'value': '{R}', 'method': IN, 'field': 'text'} ),
...             Or( {'value': '{G}', 'method': IN, 'field': 'manaCost'},
...                 {'value': '{G}', 'method': IN, 'field': 'text'} ),
...             Or( {'value': '{U}', 'method': IN, 'field': 'manaCost'},
...                 {'value': '{U}', 'method': IN, 'field': 'text'} ),
...             Or( {'value': '{W}', 'method': IN, 'field': 'manaCost'},
...                 {'value': '{W}', 'method': IN, 'field': 'text'} ),
...             Or( {'value': '{B}', 'method': IN, 'field': 'manaCost'},
...                 {'value': '{B}', 'method': IN, 'field': 'text'} ) )(db)

Valid values for 'method':
    - is: case-insensitive exact match of full string
    - in: case-insensitive text search, except for land
          where it looks for an exact (case-ignored) match with a word.
    - matches: regex match
    - gt, ge, eq, le, lt: only work for numeric fields,
                          i.e. 'convertedManaCost'

There are also a number of predicates that can be used for convenience.
These simply work by generating dictionaries similar to those seen above.

Lands that produce colourless mana:
>>> search.And( HasType(LAND),
...             TextContains("{C}") )(db)

Cheap counterspells:
>>> search.And( TextMatches("counter.*target"),
...             CMC(le=2) )(db)

Text contains the words "shuffle", "graveyard", and "library"
in any order and at any position:
>>> search.TextContains("shuffle", "graveyard", "library")(db)

Available predicates:
    - And
    - Or
    - Not
    - NameContains
    - NameMatches
    - NameIs
    - TextContains
    - TextMatches
    - CMC

"""
import operator, re

class Result(dict):
    """Class used to represent search results.

    Dictionary structure is that of the database dictionary, e.g.:
    {'swamp': {'name': 'Swamp', 'type': 'Land', ...},
     'fork': {'name': 'Fork', 'type': 'Instant', 'manaCost': '{R}{R}', ...},
     ...}

    Will provide functionality additional to that of `dict`:
    - Represents self as a set containing the card names
    - oneline() method returns formatted representations of cards
    """
    def copy(self):
        """Shallow copy as per dict.copy()"""
        return Result(super().copy())

    def add(self, d):
        """Copies itself, updates the copy with `d`, and returns the copy."""
        new = self.copy()
        new.update(d)
        return new

    def oneline(self, width=0):
        """Return a list of oneline format of cards in the result."""
        import moracle
        return [moracle.format_oneline(v, width) for v in self.values()]

"""Comparison methods.

These are functions of the form fn(db_value, desired_value).
They return a Boolean value determined by whether or not `desired_value`
matches `db_value`.
"""
# String comparison methods
IS = lambda value, desired: value.lower() == desired.lower()
def IN(value, desired):
    if type(value) == list:
        return desired in value
    else:
        return value.lower().find(desired.lower()) > -1
MATCHES = lambda value, desired: re.search(desired, value) != None
# Numeric comparison methods
LT = operator.lt
LE = operator.le
EQ = operator.eq
GE = operator.ge
GT = operator.gt

# Main search function
def search(field='name', method=IS, value=None):
    """Searches for cards which match the given condition.
    
    Returns a function which takes a database dict or Result and returns a Result.

    The Result object is dict-like.
    Keys in Result are keys from the db; values are values from the db.
    """
    def searchPred(db):
        return Result((k, v) for k, v in db.items()
                             if field in v and method(v[field], value))

    return searchPred

# Set manipulation
def And(*conditions):
    """The intersection of the results of searches satisfying `conditions`.
    
    Returns a function which takes a database dict or Result and returns a Result.
    """
    def andPred(db):
        from functools import reduce
        return reduce(lambda result, c: c(result),
                      conditions, db)

    return andPred

def Or(*conditions):
    """The union of the results of searches satisfying `conditions`.

    Returns a function which takes a database dict or Result and returns a Result.
    """
    def orPred(db):
        from functools import reduce
        return reduce(lambda result, c: result.add(c(db)),
                      conditions, Result())

    return orPred

def Not(*conditions):
    """The negation of the union of search results satisfying `conditions`.

    In other words, the result set is every item in db which does not meet
    any of the supplied conditions.

    Returns a function which takes a database dict/Result and returns a Result.
    """
    def notPred(db):
        matches = Or(*conditions)(db)
        return Result((k, v) for k, v in db.items() if k not in matches)

    return notPred

# Convenience predicates
def NameContains(string):
    return search(value=string, method=IN, field='name')

def NameMatches(regexp):
    return search(value=regexp, method=MATCHES, field='name')

def NameIs(string):
    return search(field='name', method=IS, value=string)

def TextContains(string):
    return search(value=string, method=IN, field='text')

def TextMatches(regexp):
    return search(field='text', method=MATCHES, value=regexp)

def CMC(value, **kwargs):
    """Predicate for cards with CMC meeting all of the passed conditions."""
    methods = {'lt': LT, 'le': LE, 'eq': EQ, 'ge': GE, 'gt': GT}
    conditions = [search(field='convertedManaCost', method=methods[m], value=v)
                  for m, v in kwargs.items() if v != None]
    return And(*conditions)

def ColorIdentityHas(colours):
    """Matches cards that have at least all elements of the colour identity.

    `colours` is a string containing any or all of the letters 'BGRUWC'.
    """
    return And(*(search(field='colorIdentity', method=IN, value=c)
                 for c in colours.upper()))

def ColorIdentityOnly(colours):
    """Matches cards whose colour identity is `colours` or a subset of it.

    `colours` is a string containing any or all of the letters 'BGRUW'.
    """
    notcolours = set('BRGUW').difference(colours.upper())
    return Not(*(search(field='colorIdentity', method=IN, value=c)
                 for c in notcolours))

def ColorIdentityIs(colours):
    """Matches cards that have exactly the given colour identity.
    
    `colours` is a string containing any or all of the letters 'BGRUW'.
    """
    return And(ColorIdentityHas(colours), ColorIdentityOnly(colours))
    # return And( And(*(search(field='colorIdentity', method=IN, value=c)
    #                   for c in colours)),
    #             Not(*(search(field='colorIdentity', method=IN, value=c)
    #                   for c in notcolours)) )

def HasType(t):
    """Matches cards that has type `t`.
    
    Checks 'types', 'subtypes' or 'supertypes' lists for all cards.

    Case-sensitive (for now).
    """
    return Or(search(field='types', method=IN, value=t),
              search(field='subtypes', method=IN, value=t),
              search(field='supertypes', method=IN, value=t))
