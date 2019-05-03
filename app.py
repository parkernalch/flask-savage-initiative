import flask
from cards import *
from flask import request, jsonify, render_template, redirect, url_for, session
import uuid
from os import urandom
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_sqlalchemy import SQLAlchemy

app  = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = urandom(24)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app)
# db = SQLAlchemy(app)


# class Character(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(24), default='', nullable=False)
#     tactician = db.Column(db.Integer, default=0, nullable=False) # 0, 1, 2
#     level_headed = db.Column(db.Integer, default=0, nullable=False) # 0, 1, 2
#     quick = db.Column(db.Boolean, default=False, nullable=False) # True / False
#     hesitant = db.Column(db.Boolean, default=False, nullable=False) # True / False
#     table_id = db.Column(db.Integer) # one-to-one character <-> table

#     def __init__(self, name, tactician, level_headed, quick, hesitant, table_id):
#         self.name = name
#         self.tactician = tactician
#         self.level_headed = level_headed
#         self.quick = quick
#         self.hesitant = hesitant
#         self.table_id = table_id

# class Table(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30))
#     description = db.Column(db.Text)
#     last_game = db.Column(db.DateTime)
#     next_game = db.Column(db.DateTime)
#     systemID = db.Column(db.Integer) # one-to-one table <-> system_id
#     characters = db.relationship() # many-to-one relationship table -< character
#     game_master = db.Column(db.String(24))
#     players = db.Column(db.String(24))

#     def __init__(self, name, system):
#         self.name = name
#         self.systemID = system

# class RPGSystem(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(24)) # should be unique
#     table_id = db.relationship('Table', backref='rpgsystem', lazy=True) # many-to-one relationship system -< table

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True)
#     password = db.Column(db.String(200))


party = [
    {
        'name': 'Sukorb Tsif',
        'tactician': 2
    },
    {
        'name': 'Cypher Tosen',
        'quick': 1
    },
    {
        'name': 'Garen Aldor'
    },
    {
        'name': 'Vik Naraiya'
    },
    {
        'name': 'Soombala'
    },
    {
        'name': 'Klethic Parnastalos'
    },
    {
        'name': 'Bossman McGee',
        'level_headed': 2,
        'quick': 1
    },
    {
        'name': 'Mookie Mook',
    }
]
party = BuildParty(party)
I = Initiative(party)

dbdict = {
    # 'sessionID': { 'username': uname, 'party': [<characters>] }
    'c61ffb7f-6804-47a9-a5aa-a316cab602be': {'username': 'parkernalch', 'party': party, 'tables': [] },
    'tables': {
        'hyperion-chronicle-82abd0e5': {
            'name': 'Hyperion Chronicle',
            'description': '''
            An intrepid group of explorers discover and must thwart a dark force that threatens the stability of their worlds.
            ''',
            'initiative': I
        },
        'skimmers-of-ord-82abd0e5': {
            'name': 'Skimmers of Ord',
            'description': '''
            Fortune-seekers on the world-sea brave dangers both natural and artificial in pursuit of ever-elusive Glimmer.
            ''',
            'initiative': I
        },
        'cypher-saga-82abd0e5': {
            'name': 'The Cypher Saga',
            'description': '''
            Follow our adventurers through the Ninth World, a strange, alien world built on eons of detritus from aeons past.
            ''',
            'initiative': I
        }
    },
    'users': {
        'parkernalch': {
            'latest_cookie': 'c61ffb7f-6804-47a9-a5aa-a316cab602be',
            'password': None,
            'party': party,
            'tables': []
        }
    }
}

@app.route('/login', methods=['GET', 'POST'])
def login(**kwargs):
    sessionID = request.cookies.get('InitiativeSession')

    if request.method == 'GET':
        for _,user in dbdict['users'].items():
            if user['latest_cookie'] == sessionID:
                return redirect(url_for('home'))
        return render_template("login.html")
    
    login_token = request.get_json()
    if login_token['username'] not in [key for key in dbdict['users'].keys()]:
        return redirect(url_for('login', username=False, password=False))
    
    if not check_password_hash(dbdict[login_token['username']]['password'], login_token['password']):
        return redirect(url_for('login', username=True, password=False))

    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    '''Routes user to homepage (layout.html)'''
    sessionID = request.cookies.get('InitiativeSession')
    if not sessionID:
        return redirect(url_for('cookie'))

    if sessionID in dbdict.keys():
        session = dbdict[sessionID]
        if 'party' in session.keys():
            party = session['party']
        else:
            party = []
        return render_template('layout.html', party=party, sessionID=sessionID, tableID="")
    else:
        return redirect(url_for('cookie'))

@app.route('/party', methods=['GET'])
def party():
    sessionID = request.cookies.get('InitiativeSession')
    if not sessionID:
        return redirect(url_for('cookie'))
    if sessionID not in dbdict.keys():
        return redirect(url_for('cookie'))
    
    party = dbdict[sessionID]['party']
    return render_template('party_list.html', party=party, sessionID=sessionID, tableID="")

@app.route('/<id>/party/<name>', methods=['GET'])
def GetPartyMember(id, name):
    member = {}
    if id in dbdict.keys():
        for char in dbdict[id]['party']:
            if char.name.replace(' ', '-').lower() == name:
                member = char
                return jsonify(member.Get())
    return "Member {} not found in party".format(name)

@app.route('/<id>/party/<name>', methods=['POST'])
def SetPartyMember(id, name):
    # print('starting SetPartyMember [get]: id={}, name={})'.format(id, name))
    if id not in dbdict.keys():
        # print('id not in dictionary')
        return
    
    newchar = request.get_json()

    for character in dbdict[id]['party']:
        if character.name.replace(' ','-').lower() == name:
            character.name = newchar['name']
            character.tactician = newchar['tactician']
            character.level_headed = newchar['level_headed']
            character.quick = newchar['quick']
            character.hesitant = newchar['hesitant']
            return redirect('/party')
    
    newparty = AddMemberTOParty(newchar, dbdict[id]['party'])
    dbdict[id]['party'] = newparty
    # return jsonify([character.Get() for character in newparty])
    return redirect('/party')

@app.route('/cookie', methods=['GET'])
def cookie():
    sessionID = request.cookies.get('InitiativeSession')
    if not sessionID:
        sessionID = str(uuid.uuid4())
        while sessionID in dbdict.keys():
            sessionID = str(uuid.uuid4())
        dbdict[sessionID] = {'username': None, 'party': []}

        response = redirect(url_for('home'))
        response.set_cookie('InitiativeSession', sessionID, max_age=90)

        return response
    
    if sessionID not in dbdict.keys():
        dbdict[sessionID] = {'username': None, 'party': []}
    return redirect(url_for('home'))


@app.route('/initiative', methods=['GET'])
def initiative():
    sessionID = request.cookies.get('InitiativeSession')
    if not sessionID:
        return redirect(url_for('set_cookie'))

    party = dbdict[sessionID]['party']
    dbdict[sessionID]['initiative'] = Initiative(BuildParty(party))
    dbdict[sessionID]['initiative'].Start()
    # req_data = request.get_json()
    return dbdict[sessionID]['initiative'].State() 


@app.route('/table/<id>', methods=['GET'])
def JoinTable(id):
    # renders player-side initiative page
    # print('starting /table/<id> for id={}'.format(id))
    if id not in dbdict['tables'].keys():
        return redirect(url_for('tables'))
    dbdict['tables'][id]['initiative'].Start()
    table = dbdict['tables'][id]
    party = table['initiative'].party
    round = table['initiative'].round
    return render_template("initiative.html", party=party, sessionID="", tableID=id, round=round)

@app.route('/table/<id>/next', methods=['GET'])
def next_round(id):
    if id not in dbdict['tables'].keys():
        return redirect(url_for('tables'))

    round = dbdict['tables'][id]['initiative'].round
    if round == 0:
        return redirect(url_for('JoinTable'))

    round += 1
    initiative = dbdict['tables'][id]['initiative']
    dbdict['tables'][id]['initiative'].NextRound()
    party = dbdict['tables'][id]['initiative'].party
    return render_template("initiative.html", party=party, sessionID="", tableID=id, round=round)

@socketio.on('next round')
def handle_next_round(data):
    print('Going to next round in room {}'.format(data['room']))
    # print(emit('go to next', room=data['room']))
    emit('go to next', room=data['room'])

@socketio.on('join')
def handle_join_event(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print(username + ' has entered room {}'.format(room))
    # send(username + ' has entered the room.', room=room, callback=ack)

@socketio.on('leave')
def handle_leave_event(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    print(username + ' has left room {}'.format(room))
    # send(username + ' has left the room.', room=room, callback=ack)

@app.route('/tables', methods=['GET', 'POST'])
def tables():
    if request.method == 'POST':
        tableID = str(uuid.uuid4())
        while tableID in dbdict['tables'].keys():
            tableID = str(uuid.uuid4())
        dbdict['tables'][tableID] = {
            'initiative': None,
            'name': 'new table',
            'members': []
        }

    tables = [(id, table) for id, table in dbdict['tables'].items()]
    return render_template("tables.html", tables=tables)

if __name__ == "__main__":
    # app.run()
    socketio.run(app)