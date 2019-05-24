from main import db
import models

db.drop_all()
db.create_all()

# Create Users
adam = models.User(
    username='adamnalch', 
    email='adam@email.com', 
    displayname='Adam'
    )
adam.set_password('adampassword')

parker = models.User(
    username='parkernalch',
    email='parker@email.com',
    displayname='Parker'
)
parker.set_password('parkerpassword')

db.session.add(parker)
db.session.add(adam)
db.session.commit()

# Create Character
hector = models.Character(name='Hector Barrelwaite')
hector.player_id = parker.id
beatty = models.Character(name='Elsinore Beatty', tactician=0, level_headed=2)
beatty.player_id = parker.id
eclipse = models.Character(name='The Eclipse', tactician=2, level_headed=0, quick=True, hesitant=False)
eclipse.player_id = parker.id
sukorb = models.Character(name='Sukorb Tsif')
sukorb.player_id = adam.id

db.session.add(hector)
db.session.add(beatty)
db.session.add(eclipse)
db.session.add(sukorb)
db.session.commit()

# Create System
swade = models.System("Savage Worlds Adventurer's Edition")
fifthed = models.System("Dungeons & Dragons: 5th Edition")
fourthed = models.System("Dungeons & Dragons: 4th Edition")
numenera = models.System("Numenera")
cypher = models.System("Cypher System")
strange = models.System("The Strange")

db.session.add(swade)
db.session.add(fifthed)
db.session.add(fourthed)
db.session.add(numenera)
db.session.add(cypher)
db.session.add(strange)
db.session.commit()

# Create Table
hyperion = models.Gametable(
    name='Hyperion Chronicle', 
    description='Stellar adventurers race against the clock to mount an insurrection against a dark ever-present foe')
hyperion.gamemaster_id = parker.id
hyperion.system_id = swade.id
swade.tables.append(hyperion)

cysaga = models.Gametable(
    name="The Cypher Saga",
    description="A series of one-shot adventurers set in the wondrous Ninth World"
)
cysaga.gamemaster_id = parker.id
cysaga.system_id = numenera.id
numenera.tables.append(cysaga)

skimmers = models.Gametable(
    name="Skimmers of Ord",
    description="Fortune-seekers sail the world-ocean in search of mystical artifacts that are known to rise from the forgotten depths"
)
skimmers.gamemaster_id = parker.id
skimmers.system_id = swade.id
swade.tables.append(skimmers)

db.session.add(hyperion)
db.session.add(cysaga)
db.session.add(skimmers)
db.session.commit()


hector.table_id = hyperion.id
beatty.table_id = hyperion.id
eclipse.table_id = hyperion.id
sukorb.table_id = hyperion.id

hyperion.characters.extend((hector, beatty, eclipse, sukorb))
hyperion.players.extend((parker, adam))
db.session.commit()
