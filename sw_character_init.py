class Character:
    def __init__(self, name, **kwargs):
        self.name = name
        self.tactician = kwargs.get('tactician', 0)
        self.level_headed = kwargs.get('level_headed', 0)
        self.quick = kwargs.get('quick', 0)

        self.hand = {
            'hand': [],
            'tactician': []
        }
    def DealHand(self, deck):
        cards_to_deal = 1 + self.level_headed
        tact_cards_to_deal = self.tactician
        return