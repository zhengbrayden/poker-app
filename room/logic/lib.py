
def compose_card(card): #this will be improved in the future
    return f"{card.value}{card.suit}"

def compose_hand_str(hand): #this will be improved?
    hand_str = []

    for card in hand:
        hand_str.append(compose_card(card))
    
    return ' '.join(hand_str)