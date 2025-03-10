from .deck import Deck
from .player import Player, Player_node
# we can log leavers even.
class Lobby():

    def __init__(self, leader_id, name):
        self.leader = leader_id
        self.players = {}
        self.head = None
        self.name = name
        self.big_blind = 15
        self.little_blind = 5
        self.init_helper()

    def get_pot(self):
        return self.pot

    def get_ids(self):
        #return a set of player ids
        return self.players

    def get_players(self):
        #returns a list of player objects
        players=[]

        for player_node in self.players.values():
            players.append(player_node.player)
        
        return players

    def get_stakes(self):
        return self.cur_stakes
    
    def get_river(self):
        return self.river[:]
    
    def get_cur_player(self):
        return self.cur_node.player

    def get_name(self):
        return self.name

    def get_leader(self):
        return self.leader

    def get_unfolded_list(self):
        unfolded_list = []
        unfolded_cursor = self.cur_node.next
        unfolded_list.append(self.cur_node.player)
        while unfolded_cursor != self.cur_node:

            if not unfolded_cursor.player.folded:
                unfolded_list.append(unfolded_cursor.player)

            unfolded_cursor = unfolded_cursor.next
        
        return unfolded_list

    def create_player(self, player_id):
        
        #player already in lobby or lobby has started
        if player_id in self.players or self.has_started:
            return False
        
        player = Player(player_id, self)
        player_node = Player_node(player)
        self.players[player_id] = player_node

        if self.head == None:
            self.head = player_node
            self.head.next = self.head
            self.head.prev = self.head
        else:
            #the newest player must be inserted as the big blind (head)
            player_node.next = self.head
            temp = self.head.prev
            player_node.prev = temp
            self.head.prev = player_node
            temp.next = player_node
            self.head = player_node

        return player
    
    def remove_player(self, player):

        if not self.is_player(player):
            return (0,)
        
        player_id = player.get_id()
        player_node = self.players[player_id]
        self.left_players.append(player_id)
        player_node.player.set_deleted()

        if len(self.players) == 0:
            #we want to delete the lobby
            return (1,)

        if player_id == self.leader:
            self.leader = player_node.next.player.get_id()

        if self.has_started:

            if self.cur_node == player_node:
                #equivalent to fold
                res = self.fold_player(player_node.player)
                return (2, res)
                
            else:
                return (3,)
        else:
            delete_node(player_node)
            return (4,)

    def start(self):
        
        if len(self.players) < 2:
            return (0,)

        if self.has_started:
            return (1,)

        self.has_started = True
        #remove money from blinds: head is big, head.prev is small
        self.head.player.raise_bet(self.big_blind)
        self.head.prev.player.raise_bet(self.small_blind)
        self.cur_stakes = self.big_blind
        #player after big blind goes first
        self.cur_node = self.head.next
        self.final_node = self.cur_node #stop at this guy (for now) Upon a raise, we basically go to the prev of the raiser. This works!
        self.n_unfolded = len(self.players)

        for player_node in self.players.values():
            player = player_node.player

            for i in range(2):
                player.add_card(self.deck.draw())
                
        return (2, self.head.player.get_id(), self.head.next.player.get_id()) 

    #returns a condition int, a list of folded players (in reverse order of folding), and accessory information for round and game end
    def fold_player(self, player):
        #if conditions are met

        if not self.has_started:
            return (0,)
        if player != self.cur_node.player:
            return (1,)

        player.set_folded()

        self.n_unfolded -= 1

        #end game if one man standing (special end case)
        if self.n_unfolded == 1:
            #distribute the pot
            #find the unfolded player
            winner_cursor = self.cur_node.next

            while winner_cursor.player.folded:
                winner_cursor = winner_cursor.next
    
            #return winners info. We have winners and we have amount won
            winnings = self.pot - winner_cursor.player.get_bet()
            self.reset()
            return (2, player.get_id(), winner_cursor.player.get_id(), winnings)

        #cycle to next player
        return (3, player.get_id(), self.cycle_player())

    def call_player(self, player):

        if not self.has_started:
            return (0,)
        if player != self.cur_node.player:
            return (1,)
        
        bet_amount = player.raise_bet(self.cur_stakes - player.get_bet())
        self.pot += bet_amount
        return (2, bet_amount, self.cycle_player())

    def raise_player(self, player, raise_amount):

        if not self.has_started:
            return (0,)
        if player != self.cur_node.player:
            return (1,)
        if raise_amount < 0:
            return (2,)
        #cannot raise if they dont have enough money
        bet_amount = self.cur_stakes - player.get_bet() + raise_amount

        if bet_amount > player.get_bank():
            return (3,)
        
        player.raise_bet(bet_amount)
        self.cur_stakes += raise_amount
        self.pot += bet_amount
        #we actually need to move last player back around. We just set to self. The final player does not get a turn.
        self.final_node = self.cur_node

        return (4, bet_amount, self.cycle_player())

    
    #helpers only (private member functions)
    def is_player(self, player):

        if player.get_id() in self.players and self.players[player.get_id()].player == player:
            return True

        return False

    def cycle_player(self):
        self.cur_node = self.cur_node.next

        if self.cur_node == self.final_node:
            return self.end_round()

        #ignore folded players
        while self.cur_node.player.folded:

            if self.cur_node == self.final_node:
                return self.end_round()

            self.cur_node = self.cur_node.next

        if self.cur_node.player.deleted:
            #player has left
            return (2, self.fold_player(self.cur_node.player))

        if self.cur_node.player.get_bank() == 0:
            #this is implemented outside of while loop because the only thing that this player can do is fold (if they have left). If it gets here, the player has not left
            return self.cycle_player()

        return (3,)

    def init_helper(self):
        self.has_started = False
        self.deck = Deck()
        self.river = []
        self.cur_node = None
        self.final_node = None
        self.n_unfolded = 0
        self.round = 0
        self.left_players = []
        self.cur_stakes = 0
        self.pot = self.big_blind + self.little_blind

    def reset(self):
        #set head to next
        self.head = self.head.next
        #set head to nearest non deleted player
        while self.head.player.deleted:
            self.head = self.head.next

        #remove all deleted players
        for player_id in self.left_players:
            delete_node(self.players[player_id])
            del self.players[player_id]

        #unfold all players, clear hands, clear bets
        self.head.player.reset()
        reset_cursor = self.head.next
        
        while reset_cursor != self.head:
            reset_cursor.player.reset()
            reset_cursor = reset_cursor.next

        self.init_helper()
    
    def showdown(self):
        #get players
        player_list = []
        unfolded_list = self.get_unfolded_list()
        unfolded_list.sort(key = lambda player: player.get_bet())
        player_cursor = self.head.next
        player_list.append(self.head.player)

        while player_cursor != self.head:
            player_list.append(player_cursor.player)
            player_cursor = player_cursor.next

        player_list.sort(key = lambda player: player.get_bet())

        hand_list = []
        id_list = []

        for player in unfolded_list:
            id_list.append(player.id)
            hand_list.append(player.get_hand())

        #update unfolded hands
        for player in unfolded_list:

            for card in self.river:
                player.add_card(card)
        
        #calculate each unfolded's hand
        for player in unfolded_list:
            player.calc_hand()
        
        #run down from highest betting player to lowest betting, distributing the pot accordingly. We need to test that this pot is 0 afterwards (mathematical proof and UnitTest)
        i = len(unfolded_list) - 1
        j = len(player_list) - 1
        
        winners_dict = {} #dict of winner id and winning amount
        
        while i > 0:

            if unfolded_list[i].get_bet() != unfolded_list[i-1].get_bet():
                j = calc_sidepot(j, i, player_list, unfolded_list, winners_dict, unfolded_list[i].get_bet(), unfolded_list[i-1].get_bet())
            
            i -= 1

        calc_sidepot(j, 0, player_list, unfolded_list, winners_dict, unfolded_list[0].get_bet(), 0)
        
        #remove winner's own bet from each winner's winnings
        for id in winners_dict:
            winners_dict[id] -= self.players[id].player.get_bet()
        return (0, winners_dict, id_list, hand_list)
    
    def end_round(self):
        
        if self.round == 3:
            return self.showdown()
        
        self.progress_round()
        return (1,)
    
    def progress_round(self):
        self.round += 1
        self.cur_node = self.head
        
        while self.cur_node.player.folded:
            self.cur_node = self.cur_node.next
        
        self.final_node = self.cur_node
        #find nearest unfolded person
        if self.round == 1:

            for i in range(3):
                self.river.append(self.deck.draw())

        else:
            self.river.append(self.deck.draw())

#this function does nothing if there is only one node.
def delete_node(node):
    node.prev.next = node.next
    node.next.prev = node.prev 

def create_sidepot(start, player_list, base, top):
    """
    A little complex. Basically, when there is a difference in the bets of the unfolded, 
    we know that we have a sidepot situation. What we can do is take all people
    "above the difference" and add their bets. The problem is we have unfolded people 
    as well who have some random bet in between the top and bottom number.
    So we save a j value which is the largest index of a player who was not in the previous sidepot 
    (equal to bot). We know that every person above j was already in a sidepot and can be added to every 
    subsequent sidepot
    """

    sidepot = (len(player_list) - start - 1) * (top - base)

    while player_list[start].get_bet() > base and start >= 0:
        sidepot += player_list[start].get_bet() - base 
        start -= 1

    return (sidepot,start)

#get winner's from a subset and remove losers
def get_winners(start, unfolded_list):
    winners = set()
    max_score = 0

    for i in range(start, len(unfolded_list)):
        
        if unfolded_list[i].handscore == max_score:
            #potential tie
            winners.add(unfolded_list[i])
        elif unfolded_list[i].handscore > max_score:
            winners = {unfolded_list[i]}
            max_score = unfolded_list[i].handscore
    #get rid of the losers (they might as well have folded)
    for i in range(len(unfolded_list) - 1, start - 1, - 1):
    #order of the already bet processed players does not matter.

        if unfolded_list[i] not in winners:
            temp = unfolded_list[i]
            unfolded_list[i] = unfolded_list[-1] 
            unfolded_list[len(unfolded_list) - 1] = temp
            unfolded_list.pop()
    
    return winners

#go through winners and distribute sidepot accordingly
def dist_sidepot(winners, sidepot, winners_dict):
    winnings = sidepot//len(winners)

    for player in winners:
        id = player.get_id()

        if id in winners_dict:
            winners_dict[id] += winnings
        else:
            winners_dict[id] = winnings

        player.add_vbucks(winnings)

def calc_sidepot(j, i, player_list, unfolded_list, winners_dict, top, bot):
    sidepot, j = create_sidepot(j, player_list, bot, top)
    winners = get_winners(i, unfolded_list) #potentially have someone winning 0 dollars, k we rewriting this part after sleep
    dist_sidepot(winners, sidepot, winners_dict)
    return j