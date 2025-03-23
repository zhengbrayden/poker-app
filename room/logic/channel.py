from .lobby import Lobby
from .player import Player

class Channel():
    def __init__(self, id = 0):
        self.lobbies = {}
        self.players = {}
        self.id = id

    def get_id(self):
        return self.id
    
    def get_lobby(self, name : str) -> Lobby:
        """ Get a lobby object by its name """
        if name in self.lobbies:
            return self.lobbies[name]
        
    def get_lobbies(self):
        return self.lobbies.values()
    
    def create_lobby(self, name, player_id):

        if name in self.lobbies:
            return 0
        
        if player_id in self.players:
            return 1

        lobby = Lobby(player_id, name)
        self.lobbies[name] = lobby
        player = lobby.create_player(player_id)
        self.players[player_id] = player
        return 2

    def create_player(self, name, player_id): 

        if not name in self.lobbies:
            return 0
        
        lobby = self.lobbies[name]

        if player_id in self.players:
            return 1

        player = lobby.create_player(player_id)

        if not player:
            return 2

        self.players[player_id] = player
        return 3
    
    def get_player(self, player_id):

        if player_id in self.players:
            return self.players[player_id]
    
    def delete_player(self, player): #player or player_id?
        
        if not self.is_player(player):
            return (0,)

        del self.players[player.get_id()]
        lobby = player.get_lobby() 
        res = lobby.remove_player(player)

        if res[0] == 1:
            del self.lobbies[lobby.get_name()]
            
            if len(self.lobbies) == 0:
                return (1, True)
            else:
                return (1, False)
        
        return res

    #helper functions
    def is_player(self, player):
        
        if player.get_id() in self.players and self.players[player.get_id()] == player:
            return True
        
        return False
    