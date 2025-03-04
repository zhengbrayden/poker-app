class Player():

    def __init__(self, member_id, lobby):
        self.id = member_id
        self.lobby = lobby
        self.bank = 1000
        self.hand = []
        self.handscore = 0
        self.bet = 0
        self.folded = False
        self.deleted = False
    
    def reset(self):
        self.hand = []
        self.reset_folded()
        self.bet = 0

    def set_folded(self):
        self.folded = True

    def reset_folded(self):
        self.folded = False

    def set_deleted(self):
        self.deleted = True
    
    def get_lobby(self):
        return self.lobby
    
    def get_bank(self):
        return self.bank
    
    def get_bet(self):
        return self.bet

    def get_hand(self):
        return self.hand

    def get_id(self):
        return self.id
        
    def add_vbucks(self, amount):
        self.bank += amount
    
    def add_card(self, card):
        self.hand.append(card)

    def calc_hand(self):
        self.handscore = calc_hand(self.hand)

    #raise_bet variant with no checks
    def increase_bet(self, amount):
        self.bank -= amount
        self.bet += amount

    def raise_bet(self, amount):

        if amount > self.bank:
            amount = self.bank

        self.increase_bet(amount)

        return amount

#Ok, future, wiser brayden thinks that it would be smarter to find all repeated elements, all suit classes, and only from there begin to calculate the hand.
def calc_hand(hand):
    hand.sort(key = lambda card: card.value) #makes life easier

    #check flush
    suit_subhands = {'S': [], 'H': [], 'D': [], 'C' : []}

    for card in hand:
        suit_subhands[card.suit].append(card)
    
    flush_subhand = []
    for suit_subhand in suit_subhands.values():

        if len(suit_subhand) >= 5:
            flush_subhand = suit_subhand
            break

    if flush_subhand:
        #check straight within flush
        score = calc_straight(flush_subhand)

        if score:
            return score + 9 * 10 ** 10
        
        #nothing better than flush can exist at this point
        return 6 * 10 ** 10 + calc_highcard(flush_subhand, 5)

    #check quad. Remember, our hand is sorted. We go through and count repeats. we can only have one quad. hand also has a fixed length of 7 (for now)
    repeat_count = 1

    for i in range(0, len(hand) - 1):
        
        if hand[i].value == hand[i+1].value:
            repeat_count += 1

            if repeat_count == 4:
                #quad exists
                quad_val = hand[i].value
                return 8 * 10 ** 10 + quad_val * 10 ** 8 + calc_highcard(hand, 1, {quad_val,})
                
        else:
            repeat_count = 1
    #next is full house
    #check triple. Hand is sorted. Can be more than one triple so we check from the top
    repeat_count = 1
    triple_val = None
    double_val = None
    for i in range(len(hand) - 1, 0, - 1):

        if hand[i].value == hand[i-1].value:
            repeat_count += 1

            if repeat_count == 3:
                triple_val = hand[i].value
                repeat_count = 1
                
                #full house
                if double_val:
                    return 7 * 10 ** 10 + triple_val * 10 ** 8 + double_val * 10 ** 6

            #full house
            elif repeat_count == 2 and triple_val:
                double_val = hand[i].value
                return 7 * 10 ** 10 + triple_val * 10 ** 8 + double_val * 10 ** 6

        #First and only double, set it to double
        else:

            if repeat_count == 2 and not double_val:
                double_val = hand[i + 1].value

            repeat_count = 1

    #check straight
    score = calc_straight(hand)

    if score:
        return score * 10 ** 8 + 5 * 10 ** 10

    if triple_val:

        return 4 * 10 ** 10 + triple_val * 10 ** 8 + calc_highcard(hand, 2, {triple_val,})

    #two pair, pair, and high card
    repeat_count = 1
    double_val = None

    for i in range(len(hand) - 1, 0, - 1):
        
        if hand[i].value != hand[i-1].value:
            repeat_count = 1
            continue
        
        
        if double_val:
            ddouble_val = hand[i].value
            return 3 * 10 ** 10 + double_val * 10 ** 8 + ddouble_val * 10 ** 6 + calc_highcard(hand, 1, {double_val, ddouble_val})
            
        double_val = hand[i].value
        repeat_count = 1
    
    if double_val:
        return 2 * 10 ** 10 + double_val * 10 ** 8 + calc_highcard(hand, 3, {double_val,})
    
    #high card
    return calc_highcard(hand, 5) + 1 * 10 ** 10

def calc_highcard(cards, quantity, exceptions = set()): #cards should be sorted

    #just use the length of cards as quant
    if quantity == 0: 
        quantity = len(cards)

    assert quantity <= 5

    score = 0 
    num_cards = 0

    for i in range(len(cards) -1, -1, -1):

        if num_cards == quantity:
            break

        card_val = cards[i].value

        if card_val not in exceptions:
            num_cards += 1
            score += card_val * 10 ** ((quantity - num_cards) * 2)

    return score

#determines if straight exists and returns the highcard portion of the score of such a straight if it does
def calc_straight(cards):
    straight_count = 1

    for i in range(len(cards) - 1, 0, -1): 

        if cards[i].value - cards[i -1].value > 1:
            straight_count = 1
            continue

        straight_count += 1

        #a straight exists
        if straight_count == 5: 
            return cards[i + 3].value

#DATA STRUCTURES
class Player_node():
    
    def __init__(self, player):
        #public
        self.player = player
        self.next = None
        self.prev = None