from main import db
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):
    __tablename__ = 'USER'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    displayname = db.Column(db.String(48), nullable=True)
    password = db.Column(db.String(1024), nullable=False)
    characters = db.relationship('Character', backref='player', lazy='select')
    owned_tables = db.relationship('Gametable', backref='gamemaster', lazy='select')
    authenticated = db.Column(db.Boolean, default=False)
    # joined_tables is a many-to-many relationship to Table through playertable

    # def __init__(self, username, email, password):
    #     self.username = username
    #     self.email = email
    #     self.password = generate_password_hash(password)
    def __repl__(self):
        return "<User {}>".format(self.email)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def is_active(self):
        return True
    
    def get_id(self):
        return self.id
    
    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def __login(self, password):
        return check_password_hash(self.password, password)

class Character(db.Model):
    __tablename__ = 'CHARACTER'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('USER.id'))
    table_id = db.Column(db.Integer, db.ForeignKey('GAMETABLE.id'))
    name = db.Column(db.String(24), default='', nullable=False)
    tactician = db.Column(db.Integer, default=0, nullable=False) # 0, 1, 2
    level_headed = db.Column(db.Integer, default=0, nullable=False) # 0, 1, 2
    quick = db.Column(db.Boolean, default=False, nullable=False) # True / False
    hesitant = db.Column(db.Boolean, default=False, nullable=False) # True / False

    def __init__(self, name, tactician=0, level_headed=0, quick=False, hesitant=False, table_id=None):
        self.name = name
        self.tactician = tactician
        self.level_headed = level_headed
        self.quick = quick
        self.hesitant = hesitant
        self.table_id = table_id

    def __addToTable(self, table_id):
        self.table_id = table_id

playertable = db.Table('PLAYERTABLE',
    db.Column('player_id', db.Integer, db.ForeignKey('USER.id')),
    db.Column('table_id', db.Integer, db.ForeignKey('GAMETABLE.id'))
    )

class Gametable(db.Model):
    __tablename__ = 'GAMETABLE'
    id = db.Column(db.Integer, primary_key=True)
    characters = db.relationship('Character', backref='gametable', lazy='select')
    gamemaster_id = db.Column(db.Integer, db.ForeignKey('USER.id'))
    players = db.relationship('User', secondary=playertable, backref='joined_tables', lazy='select')
    system_id = db.Column(db.Integer, db.ForeignKey('SYSTEM.id'))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    last_game = db.Column(db.DateTime)
    next_game = db.Column(db.DateTime)

    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def __updateNextGame(self, nextgame):
        self.last_game = self.next_game
        self.next_game = nextgame

    def convert(self):
        output = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'last_game': self.last_game,
            'next_game': self.next_game
        }
        return output


class System(db.Model):
    __tablename__ = 'SYSTEM'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    tables = db.relationship('Gametable', backref='system', lazy=True)

    def __init__(self, name):
        self.name = name

def tableToDict(gametable):
    output = {
        'id': gametable.id,
        'name': gametable.name,
        'description': gametable.description,
        'characters': gametable.characters,
        'gamemaster_id': gametable.gamemaster_id,
        'players': gametable.players,
        'system_id': gametable.system_id,
        'last_game': gametable.last_game,
        'next_game': gametable.next_game
    }
    return output

def userToDict(user):
    output = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'displayname': user.displayname,
        'characters': user.characters,
        'owned_tables': user.owned_tables
    }
    return output

def charToDict(character):
    output = {
        'id': character.id,
        'player': character.player_id,
        'table': character.table_id,
        'name': character.name,
        'tactician': character.tactician,
        'level_headed': character.level_headed,
        'quick': character.quick,
        'hesitant': character.hesitant
    }
    return output