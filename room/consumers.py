import json

from channels.generic.websocket import AsyncWebsocketConsumer

from django.contrib.auth.models import User
from .storage import channel, messages
from .logic.lib import compose_hand_str
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name'] #the slug
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        command = data['command']

        if command == 'start':
            # Start lobby if conditions are met and set start message
            player = channel.get_player(self.user.id)
            lobby = player.get_lobby()

            #check if user issuing start command is leader
            if lobby.get_leader() != self.user.id:
                return
            
            res_code = lobby.start()

            if res_code == 0:
                #the number of players is not sufficient in the lobby
                message = 'Cannot start the lobby since there is not enough players'
                #store message
                messages.add(lobby.get_name(), message)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'plain_message',
                        'message': message
                    }
                )
                return
            elif res_code == 1:
                #the game is already started (ignore this as it shouldnt be possible)
                return
            
            #ok so the game has started and we need to update our players. First compose a common message
            player_names = []
            players = lobby.get_unfolded_list()
            player_ids = [player.get_id() for player in players]
            #require the username current player
            cur_id = lobby.get_cur_player().get_id()
            #require the usernames of big blind and little blind
            small_id = lobby.get_little_blind().get_id()
            big_id = lobby.get_big_blind().get_id()
            stake = lobby.get_stakes()
            big_blind_name = await self.get_name(big_id)
            small_blind_name = await self.get_name(small_id)
            cur_name = await self.get_name(cur_id)
            
            for i in range(len(player_ids) - 1):
                username = await self.get_name(player_ids[i]) #should we be running this inside of a loop? yes but also it doesnt matter
                player_names.append(username)
                player_names.append(' => ')
            
            username = await self.get_name(player_ids[-1])

            player_names.append(username)
            player_names = "".join(player_names)
            message = f'Game has started. Big blind: "{big_blind_name}", Small blind: ' + \
            f'"{small_blind_name}", Current player: "{cur_name}", Stake: "{stake}", ' + \
            f'Turn order: {player_names}.'
            messages.add(message)

            await self.channel_layer.group_send(
                #we need to send . . . different things to everyone, but a common message
                self.room_group_name,
                {
                    'type': 'start_message',
                    'message': message
                }
            )

    async def start_message(self, event):
        message = event['message']
        player = channel.get_player(self.user.id)
        hand = compose_hand_str(player.get_hand())
        bet = player.get_bet()
        balance = player.get_bank()

        await self.send(text_data=json.dumps({
            'command': 'start',
            'hand': hand,
            'stake': bet,
            'balance': balance,
            'message': message
        }))

    # Receive message from room group
    async def plain_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'plain'
        }))

    @database_sync_to_async
    def get_name(self, id):
        return User.objects.get(id = id).username
