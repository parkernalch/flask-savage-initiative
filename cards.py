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
        self.active = kwargs.get('active', 0)
        #Tactician: draw x many extra cards and you can distribute
        self.tactician = kwargs.get('tactician', 0)
        
        #Level Headed: draw x many extra cards for yourself, pick one
        self.level_headed = kwargs.get('level_headed', 0)

        #Quick: Re-draw cards five or lower
        self.quick = kwargs.get('quick', 0)

        #Hesitant: Draw two cards and pick lower
        self.hesitant = kwargs.get('hesitant', 0)

        self.color = kwargs.get('color', 'black')
        self.icon = kwargs.get('icon', 'fas fa-user')

        if 'cards' in kwargs:
            self.cards = cards
        else:
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
            'cards': self.cards,
            'icon': self.icon,
            'color': self.color
        }
        return output

    def MaxCard(self):
        maxCard = self.cards['hand'][0]
        maxVal = GetCardValue(maxCard)
        for card in self.cards['hand']:
            newVal = GetCardValue(card)
            if newVal > maxVal:
                maxCard = card
                maxVal = newVal
        return maxVal

class Deck:
    def __init__(self, cards=None, nextIndex=None):
        if cards is not None:
            self.cards = cards
        else:
            self.cards = []
            ## init deck
            for suit in ['s', 'h', 'd', 'c']:
                for i in range(2, 15):
                    self.cards.append(f'{i}{suit}')
            self.cards.append('15r')
            self.cards.append('15b')
            self.Shuffle()

        if nextIndex is not None:
            self.nextIndex = nextIndex
        else:
            self.nextIndex = 0

        self.nextCard = self.cards[self.nextIndex]

    def State(self):
        output = {
            'cards': self.cards,
            'nextindex': self.nextIndex,
        }
        return output

    def Shuffle(self):
        for i in range(1000):
            i1 = randint(0, 53)
            i2 = randint(0, 53)
            
            temp = self.cards[i1]
            self.cards[i1] = self.cards[i2]
            self.cards[i2] = temp

        self.nextIndex = 0
        self.nextCard = self.cards[self.nextIndex]
        return 

    def Deal(self):
        card = self.nextCard
        self.nextIndex += 1
        if self.nextIndex >= len(self.cards):
            self.Shuffle()
        self.nextCard = self.cards[self.nextIndex]
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

    def Load(self, cards, nextindex):
        self.cards = cards
        self.nextIndex = nextindex
        self.nextCard = self.cards[self.nextIndex]
        return

class Initiative:
    def __init__(self, party, deck=None, round=None, needShuffle=None):
        self.party = party
        # DECK ================
        if deck is not None:
            self.deck = deck
        else:
            self.deck = Deck()
        # ROUND ===============
        if round is not None:
            self.round = round
        else:
            self.round = 0
        # SHUFFLE ============
        if needShuffle is not None:
            self.needShuffle = needShuffle
        else:
            self.needShuffle = 0
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
            self.needShuffle = 0

        for character in self.party:
            character.DealHand(self.deck)
            for c in character.cards['hand'] + character.cards['tactician']:
                if c in ['15b', '15r']:
                    self.needShuffle = 1
        self.round += 1 
        self.InitiativeOrder()
        for i, char in enumerate(self.party):
            if i==0:
                char.active = 1
            else:
                char.active = 0
        return self.State()
    
    def State(self):
        output = {
            "party": []
        }
        self.InitiativeOrder()
        for i, char in enumerate(self.party):
            if i==0:
                char.active = 1
            else:
                char.active = 0
        for i in range(len(self.party)):
            character = self.party[i]
            newchar = {
                'name': character.name,
                'cards': character.cards,
                'tactician': character.tactician,
                'level_headed': character.level_headed,
                'quick': character.quick,
                'hesitant': character.hesitant,
                'active': character.active,
                'icon': character.icon,
                'color': character.color
            }
            output['party'].append(newchar)
        output['round'] = self.round
        output['deck'] = self.deck.State()
        output['needshuffle'] = self.needShuffle
        return output
    
    def SerializeParty(self):
        output = []
        for character in self.party:
            output.append(character.Get())
        return output
    
    def InitiativeOrder(self):
        # orderedparty = sorted((character for character in self.party), key=lambda x: max( GetCardValue(x.cards['hand'][0]) for card in x.cards['hand']), reverse=True)
        orderedparty = sorted((character for character in self.party), key=lambda x: x.MaxCard(), reverse=True)
        # print([f'{character.name} with {character.cards["hand"][0]}: {GetCardValue(character.cards['hand'][0])}' for character in party])
        self.party = orderedparty
        # print([character.name for character in self.party])
        # for character in self.party:
        #     print(character.name)
        #     print(character.cards['hand'][0])
        #     print(GetCardValue(character.cards['hand'][0]))
        #     print('================')
        return

def BuildParty(party):
    partyList = []
    for character in party:
        partyList = AddMemberToParty(character, partyList)
    return partyList

def AddMemberToParty(member, party):
    update = False
    index = -1
    # print(member)
    # print(party)
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
    if 'active' in member.keys():
        newchar.active = member['active']

    if 'color' in member.keys():
        newchar.color = member['color']
    if 'icon' in member.keys():
        newchar.icon = member['icon']

    if 'cards' in member.keys():
        newchar.cards = member['cards']

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