from .logic.channel import Channel

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

slug_generator = slugGenerator()
channel = Channel()
