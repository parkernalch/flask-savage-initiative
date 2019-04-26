from random import randint
# from sw_character_init import Character

class Character:
    '''
    Tactician: draw x many extra cards and you can distribute
    Level Headed: draw x many extra cards for yourself, pick one
    Quick: Re-draw cards five or lower
    Hesitant: Draw two cards and pick lower
    '''
    def __init__(self, name, **kwargs):
        self.name = name
        #Tactician: draw x many extra cards and you can distribute
        self.tactician = kwargs.get('tactician', 0)
        
        #Level Headed: draw x many extra cards for yourself, pick one
        self.level_headed = kwargs.get('level_headed', 0)

        #Quick: Re-draw cards five or lower
        self.quick = kwargs.get('quick', 0)

        #Hesitant: Draw two cards and pick lower
        self.hesitant = kwargs.get('hesitant', 0)

        self.cards = {
            'hand': [],
            'tactician': []
        }
        return

    def EmptyHand(self):
        self.cards = {
            'hand': [],
            'tactician': []
        }
        return

    def DealHand(self, deck):
        self.EmptyHand()

        ## Deal Hand
        if self.hesitant:
            cards = deck.DealN(2)
            if int(cards[0][:-1]) > int(cards[1][:-1]):
                temp = cards[0]
            else:
                temp = cards[1]
                
            self.cards['hand'].append(temp)

        else:
            for i in range(1 + int(self.level_headed)):
                while True:
                    temp = deck.Deal()

                    if self.quick and int(temp[:-1]) > 5:
                        self.cards['hand'].append(temp)
                        break
                    elif not self.quick:
                        self.cards['hand'].append(temp)
                        break                

        self.cards['hand'] = sorted((card for card in self.cards['hand']), key=lambda x: GetCardValue(x), reverse=True)

        ## Handle Tactician
        self.cards['tactician'] = deck.DealN(self.tactician)
        return
    
    def Get(self):
        output = {
            'name': self.name,
            'tactician': self.tactician,
            'level_headed': self.level_headed,
            'quick': self.quick,
            'hesitant': self.hesitant,
            'cards': self.cards
        }
        return output

class Deck:
    def __init__(self):
        self.cards = []

        ## init deck
        for suit in ['s', 'h', 'd', 'c']:
            for i in range(2, 15):
                self.cards.append(f'{i}{suit}')
        self.cards.append('15r')
        self.cards.append('15b')
        self.Shuffle()

        self.nextCard = self.cards[0]

    def Shuffle(self):
        for i in range(1000):
            i1 = randint(0, 53)
            i2 = randint(0, 53)
            
            temp = self.cards[i1]
            self.cards[i1] = self.cards[i2]
            self.cards[i2] = temp
        return 

    def Deal(self):
        card = self.nextCard
        try:
            self.nextCard = self.cards[self.cards.index(card) + 1]
        except IndexError:
            self.Shuffle()
            self.nextCard = self.cards[0]
        return card

    def DealN(self, count):
        hand = []
        for i in range(count):
            hand.append(self.Deal())
        return hand

    def Pick(self, card):
        ind = self.cards.index(card)
        self.cards = [card] + self.cards[:ind] + self.cards[ind+1:]
        return

    def Load(self, cards, nextcard):
        self.cards = cards
        self.nextCard = nextcard
        return

class Initiative:
    def __init__(self, party):
        self.deck = Deck()
        self.party = party
        self.round = 0
        self.needShuffle = False
        return
    def Start(self):
        self.deck = Deck()
        return self.NextRound()
    def NextRound(self, **kwargs):
        if 'round' in kwargs.keys():
            self.round = kwargs['round']

        if 'deck' in kwargs.keys():
            # print(kwargs['deck']['cards'])
            # print(kwargs['deck']['nextCard'])
            # print(kwargs['deck']['needShuffle'])
            self.deck.Load(kwargs['deck']['cards'], kwargs['deck']['nextCard'])
            self.needShuffle = kwargs['deck']['needShuffle']

        if self.needShuffle:
            #print('shuffling')
            self.deck.Shuffle()
            self.needShuffle = False

        for character in self.party:
            character.DealHand(self.deck)
            for c in character.cards['hand'] + character.cards['tactician']:
                if c in ['15b', '15r']:
                    self.needShuffle = True
        self.round += 1 
        self.InitiativeOrder()
        return self.State()
    def State(self):
        output = {
            "party": []
        }
        for character in self.party:
            newchar = {
                'name': character.name,
                'cards': character.cards,
                'tactician': character.tactician,
                'level_headed': character.level_headed,
                'quick': character.quick,
                'hesitant': character.hesitant
            }
            output['party'].append(newchar)
        # print('''
        # === Round {round} ===
        # {output}
        # === END ===
        # '''.format(round=self.round, output=output))
        # output['deck'] = {
        #     'cards': self.deck.cards,
        #     'nextCard': self.deck.nextCard,
        #     'needShuffle': self.needShuffle
        # }
        output['round'] = self.round
        return output
    def SerializeParty(self):
        output = []
        for character in self.party:
            output.append(character.Get())
        return output
    def InitiativeOrder(self):
        orderedparty = sorted((character for character in self.party), key=lambda x: GetCardValue(x.cards['hand'][0]), reverse=True)
        self.party = orderedparty
        return

def BuildParty(party):
    partyList = []
    for character in party:
        partyList = AddMemberTOParty(character, partyList)
    return partyList

def AddMemberTOParty(member, party):
    update = False
    index = -1
    # print(member)
    for i, char in enumerate(party):
        if member['name'] == char.name:
            index = i
            update = True
            break

    newchar = Character(member['name'])
    if 'tactician' in member.keys():
        newchar.tactician = member['tactician']
    if 'quick' in member.keys():
        newchar.quick = member['quick']
    if 'level_headed' in member.keys():
        newchar.level_headed = member['level_headed']
    if 'hesitant' in member.keys():
        newchar.hesitant = member['hesitant']
    
    if update and index >= 0:
        party[index] = newchar
    else:
        party.append(newchar)
    return party

def GetCardValue(card):
    value = float(card[:-1])
    suit = card[-1:]
    trailer = (ord(suit) - 20) / 100.0
    return value + trailer

# party = [
#     {
#         'name': 'Sukorb',
#         'tactician': 2
#     },
#     {
#         'name': 'Cypher',
#         'quick': 1
#     },
#     {
#         'name': 'Garen'
#     },
#     {
#         'name': 'Vik'
#     },
#     {
#         'name': 'Soombala'
#     },
#     {
#         'name': 'Klethic'
#     },
#     {
#         'name': 'Bossman',
#         'level_headed': 2,
#         'quick': 1
#     }
# ]


# P = Party(party)

# init = Initiative(P)
# init.Start()

# i = input()
# while i == '':
#     init.NextRound()
#     i = input()