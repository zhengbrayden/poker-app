from .logic.channel import Channel
from collections import deque

class slugGenerator():
    def __init__(self):
        self.name2slug = {}
        self.slug2name = {}
        self.slugcount = -1
    def create_slug(self, name):
        self.slugcount += 1
        self.name2slug[name] = self.slugcount
        self.slug2name[str(self.slugcount)] = name
        return self.slugcount

class Messages():
    def __init__(self):
        self.messages_by_lobby = {}
    
    def add(self, lobby_name, message):

        if lobby_name not in self.messages_by_lobby:
            self.messages_by_lobby[lobby_name] = deque()
        
        messages = self.messages_by_lobby[lobby_name]
        messages.append(message)

        if len(messages) > 25 : 
            messages.popleft()

    def delete(self, lobby_name): 
        del self.messages_by_lobby[lobby_name]

    def get(self, lobby_name):
        return self.messages_by_lobby[lobby_name]

messages = Messages()
slug_generator = slugGenerator()
channel = Channel()
