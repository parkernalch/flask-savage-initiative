# Savage Initiative
[Check it out!](https://swinit.herokuapp.com)
Using the rules from Savage Worlds RPG by Pinnacle Entertainment Group (PEG), this site stores and tracks characters and monsters through initiative. 
Unlike d20-based systems like Pathfinder and Dungeons & Dragons, Savage Worlds uses a deck of 54 playing cards (including jokers).

### Suit Order: ♠ > ♥ > ♦ > ♣

# Characters
### Name
The character's display name on the site
### Edges
- **Level Headed Edges**
	- *Level Headed*: 
		- Character receives 1 extra card and chooses which to act on
	- *Improved Level Headed*: 
		- Character receives 2 extra cards and chooses which to act on
- **Tactician Edges**
	- *Tactician:*
		- Character receives 1 card per round that he/she can distribute to an allied Extra in Command range
	- *Battle Master:*
		- Character receives 2 cards per round that he/she can distribute to an allied Extra in Command range
- **Quick Edge**
	- Character re-draws cards that are five and lower

### Hindrances
- **Hesitant**
	- Character receives 1 extra card and must act on the lower one

### Other Properties
- **Active**
	- binary true/false value that tells the webapp which character is current in initiative order
- **Color**
	- String color name for player icon customization
- **Icon**
	- FontAwesome classname for player icon, set by picking one of 36 options
- **Cards**
	- HAND: Array of string values of cards in hand
	- TACTICIAN: Array of string values of cards dealt to characters with a Tactician-type edge
## Methods
### DealHand
- Empties hand, then resets the CARDS attribute with a round of new cards based on Edges and Hindrances present
### Get
- Serializes the Character-class object into a python dictionary, which can then be passed as JSON to the webpage
### MaxCard
- Returns the value of the highest-value card in hand for use in establishing initiative order
### EmptyHand
- Sets the CARDS attribute to a dict containing two blank lists: Hand, and Tactician

# Deck
## Properties
### Cards
	- 54-card array of string representations of each card
### NextIndex
	- Int index of card beyond most recently dealt card
### NextCard
	- String value of the cards array at NextIndex
## Methods
### State
	- Serializes the Deck-class object into a python dict which can be passed to the page as JSON
### Shuffle
	- Randomly swaps two indices in a 1000-iteration loop to shuffle the deck
### Deal
	- return the card string for the 'top' card in the deck
### DealN
	- Return list of N cards from the 'top' of the deck
### Pick [unused]
	- Find card within deck and deal it specifically
### Load
	- Instantiate the deck from a list of cards and a nextIndex
	- Allows for persistent decks amidst the GET POST cycle


# Initiative
## Properties
### Deck
	- Deck-class object, defined above
### Round
	- Integer value of the current round (counted since last Start())
### NeedShuffle
	- Boolean value indicating whether or not NextRound() should shuffle the deck
		- In Savage Worlds, decks must be shuffled when any Joker has been dealt (as well as when the deck runs out of cards)
### Party
	- List of Character-class objects representing the active members in the current Initiative
## Methods
### Start
	- Gets a 'fresh' deck object
	- Calls NextRound
### NextRound
	- Takes in Round and Deck as possible kwargs
	- Calls DealHand for each character in Party
	- Increments the Round
	- Sorts the Party based on MaxValue of each Party member's cards
	- Returns the Serialized Dictionary from State()
### State
### SerializeParty
### InitiativeOrder

# Other Methods
### BuildParty
### AddMemberToParty
### GetCardValue
