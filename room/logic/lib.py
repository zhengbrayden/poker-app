import discord
import re

async def ping_msg(message, content, embed=None):
    await message.channel.send(mention(message.author.id)  + ' ' + content, embed = embed)

def get_channel(message, Channels): 

    if message.channel.id in Channels:
        return Channels[message.channel.id]
        
def mention(id):
    return '<@' + str(id) + '>'

def compose_card(card): #this will be improved in the future
    return f"{card.value}{card.suit}"

def compose_hand_str(hand): #this will be improved?
    hand_str = []

    for card in hand:
        hand_str.append(compose_card(card))
    
    return ' '.join(hand_str)

# def compose_players_str(client, player_ids):
#     player_names=[]

#     if len(player_ids) == 1:
#         return client.get_user(player_ids[i]).name
    
#     for i in range(len(player_ids) - 2):
#         player_names.append(client.get_user(player_ids[i]).name)
#         player_names.append(', ')

#     player_names.append(client.get_user(player_ids[len(player_ids) - 2]).name)
#     player_names.append(" and ")
#     player_names.append(client.get_user(player_ids[len(player_ids) - 1]).name)
#     return "".join(player_names)

def get_lobby_name_by_id(channel, id):
    return channel.get_player(id).get_lobby().get_name()

def get_call_content():

    pass

def get_cycle_content(res, client, lobby):
    flag = res[0]
    embed=None
    content=[]

    if flag == 0:
        #the game has ended by showdown
        #parse result object
        winners_dict = res[1]
        unfolded_list = res[2]
        hand_list = res[3]
        embed= discord.Embed(title="Showdown")

        #for every player add their hands.
        for i in range(len(unfolded_list)):
            unfolded_id=unfolded_list[i]
            hand_str=compose_hand_str(hand_list[i])
            embed.add_field(name=client.get_user(unfolded_id).name + "'s Hand", value=hand_str, inline = False)

        #add a field for every winning
        for id, winnings in winners_dict.items():
            embed.add_field(value=winnings, name = f"{client.get_user(id).name}'s winnings", inline = False)

        embed.set_footer(text="To play again, reuse the 'start' command.")
    elif flag == 1: # Means we have simply moved to another round. WE need to output the river, and the person's turn, maybe the pot?
        embed= discord.Embed(title = "Game Update")
        embed.add_field(name='Common cards', value = compose_hand_str(lobby.get_river()))
        embed.add_field(value = mention(lobby.get_cur_player().get_id()), name = "Next Player")
        embed.add_field(value = f"{lobby.pot}", name = "Pot")

    elif flag == 2: # someone has folded
        res = res[1]
        fold_res = get_folded_content(res, client, lobby, False)
        content += fold_res[0]
        embed = fold_res[1]
    elif flag == 3: # it is simply next person's turn
        embed= discord.Embed()
        next_player=lobby.get_cur_player()
        embed.add_field(value = mention(next_player.get_id()), name = "Next Player")
        diff=lobby.get_stakes() - next_player.get_bet()

        if diff > 0:
            embed.set_footer(text = f'You are short ${diff}.')

    return (content, embed)

def get_folded_content(res, client, lobby, is_command):
    flag = res[0]

    embed=None
    if flag == 0:
        content = [f"Cannot fold as the lobby '{lobby.get_name()}' has not started"]
    elif flag == 1:
        content = [f"Cannot fold as it is not your turn!"]
    else:
        
        if is_command:
            content = ["You have folded."]
        else:
            fold_id = res[1]
            content = f"{client.get_user(fold_id).name} has folded."

        if flag == 2:
            #game has ended by simple folding
            #parse result object
            winner_id=res[2]
            winnings=res[3]
            embed= discord.Embed(title="Game End")
            embed.add_field(name="Winner", value=client.get_user(winner_id).name)
            embed.add_field(name="Winnings:", value=f"${winnings}")
            embed.set_footer(text="To play again, reuse the 'start' command.")
        elif flag == 3:
            res = res[2]
            cycle_res = get_cycle_content(res, client, lobby)
            cycle_content = cycle_res[0]
            content += cycle_content
            embed = cycle_res[1]

    return (content, embed)
