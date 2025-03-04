import random

class Deck():
    def __init__(self):

        self.set = set()
        self.list = []
        def append_cards(suit):
            for value in range(2,14):
                card = Card(suit, value) 
                self.set.add(card) 
                self.list.append(card) 
                
        append_cards('H')
        append_cards('S')
        append_cards('D')
        append_cards('C')

    def draw(self):
        rand_index = random.randint(0, len(self.list) - 1)
        drawn_card = self.list[rand_index]
        self.list[rand_index] = self.list[len(self.list) - 1]
        self.list.pop()
        self.set.remove(drawn_card)
        return drawn_card

class Card():
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value