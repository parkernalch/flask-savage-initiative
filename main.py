import flask
from cards import *
from flask import request, jsonify, render_template, redirect, url_for, session, g
from os import urandom
import random, string
# from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import SocketIO, join_room, leave_room, send, emit, rooms
# from flask_sqlalchemy import SQLAlchemy
# import models as m
import json
import redis

app  = flask.Flask(__name__)
app.config['DEBUG'] = True

app.config['SECRET_KEY'] = urandom(24)
socketio = SocketIO(app)

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mHCbBr0EbK:r5BX9RsjWu@remotemysql.com:3306/mHCbBr0EbK'
# db = SQLAlchemy(app)

r = redis.Redis(decode_responses=True)
r.flushall()

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     req_data = request.get_json()
#     # POST
#     # check hashed password against pw database
#     # reroute to current page
#     if request.method == 'POST':
#         uname = req_data['username']
#         pwd = req_data['password']
#         user = m.User.query.filter(m.User.username == uname).first()

#         if check_password_hash(user.password, pwd):
#             user.authenticated = True
#             session['user'] = user.username
#             # return '{} successfully logged in as {}'.format(user.displayname, user.username)
#             responseUser = {'displayname': user.displayname, 'username': user.username }
#             return jsonify(responseUser)
#         return 'login failed'

#     # GET
#     # display login screen
#     return render_template("login.html")

# @app.route('/logout', methods=['POST'])
# def logout():
#     print('starting logout')
#     req_data = request.get_json()
#     # uname = req_data['username']
#     session.pop('user', None)
#     return '{} successfully logged out'.format(req_data['username'])

@app.route('/', methods=['GET'])
def index():
    # check if logged in
    user = None
    if 'user' in session:
        print('user in session')
        # queriedUser = m.User.query.filter(m.User.username == session['user']).first()
        # user = queriedUser.displayname
    # display homepage
    else:
        print('user not in session')
        user = ''.join(random.choices(string.ascii_letters, k=10))
        session['user'] = user

    if 'encounter' in session:
        encounter = {
                'party': []
            }
        session['encounter'] = encounter

    return render_template('layout.html', user=user)

@app.route('/home', methods=['GET'])
def home():
    # display homepage
    if 'user' in session:
        print('user in session ::home::')
        user = session['user']
        emit('leave', { 'user': user , 'room': 'all' }, namespace="/")
    else:
        user = None
        print('user not in session ::home::')
    return render_template('home.html', user=user)

@app.route('/encounter/load', methods=['POST'])
def loadEncounter():
    print('loading encounter from localstorage')
    loadedParty = request.get_json()
    party = loadedParty['party']

    encounter = {
        'party': party
    }
    session['encounter'] = encounter
    return render_template("encounter.html", party=session['encounter']['party'])

@app.route('/encounter', methods=['GET', 'POST'])
def encounter():
    # POST
    # create new encounter object for user
    # display list of available encounters
    if request.method == 'POST':
        modalChar = request.get_json()

        party = session['encounter']['party']
        # print('found party:')
        # print(party)
        # if modalChar['oldname'] in [char['name'] for char in party]:
        
        charIndex = -1
        for i, char in enumerate(party):
            if char['name'] == modalChar['oldname']:
                charIndex = i
        
        if charIndex >= 0:
            # Update entry with name == oldname
            if modalChar['type'] == 'update':
                party[charIndex] = modalChar
            if modalChar['type'] == 'delete':
                party = [member for member in party if not member['name'] == modalChar['oldname'] ]
        else:
            # Add the new character
            party.append(modalChar)

        # session['encounter']['party'] = party
        # encounter = session['encounter']
        encounter = {
            'party': party
        }
        session['encounter'] = encounter
        # print(session['encounter']['party'])
        return render_template("encounter.html", party=session['encounter']['party'])

    # GET
    if 'encounter' in session:
        encounter = session['encounter']
        # print(encounter)
        # print('found encounter in session')
    else:
        encounter = {
            'party': []
        }
        session['encounter'] = encounter
        # print(encounter)
        # print('encounter not in session')
    return render_template("encounter.html", party=encounter['party'])

@app.route('/encounter/initiative/start', methods=['GET'])
def encounterInitiative():
    # req_data = request.get_json()

    party = session['encounter']['party']
    # print('Found and Built party:')
    initParty = BuildParty(party)
    print(initParty)

    initiative = Initiative(initParty)
    initiative.Start()
    # print('Initiative State:')
    # print(initiative.State())

    state = initiative.State()

    return render_template("initiative.html", party=state['party'], round=state['round'], initiative=state)

@app.route('/encounter/initiative/next', methods=['POST'])
def encounterInitiativeNext():
    req_data = request.get_json()
    party = BuildParty(req_data['party'])
    round = req_data['round']
    deck = Deck(req_data['deck']['cards'], req_data['deck']['nextindex'])
    needshuffle = req_data['needshuffle']

    initiative = Initiative(party, deck, round, needshuffle).NextRound()

    return render_template("initiative.html", party=initiative['party'], round=initiative['round'], initiative=initiative)

@app.route('/encounter/initiative/update', methods=['POST'])
def encounterInitiativeUpdate():
    req_data = request.get_json()
    party = BuildParty(req_data['party'])
    round = req_data['round']
    deck = Deck(req_data['deck']['cards'], req_data['deck']['nextindex'])
    needshuffle = req_data['needshuffle']

    initiative = Initiative(party, deck, round, needshuffle).State()

    return render_template("initiative.html", party=initiative['party'], round=initiative['round'], initiative=initiative)

def UpdateRedisInitiative(id, nextround=True):
    fetchID = id[-6:]
    party = FetchPartyByID(fetchID)
    deck = FetchDeckByID(fetchID)
    round = int(FetchRoundByID(fetchID))
    init = Initiative(
        party,
        Deck(deck['cards'], int(deck['nextindex'])),
        round,
        deck['needshuffle']
    )
    if nextround:
        print("getting next round")
        init.NextRound()

    # Add Party to Redis cache under key of newTableID
    truncID = id[-6:]
    
    # SET PARTY
    
    r.delete(f"{truncID}:party")
    for i, char in enumerate(init.State()['party']):
        r.sadd(f"{truncID}:party", char['name'])

        prefix = f"{truncID}:{char['name']}"
        # hesitant
        r.set(f"{prefix}:hesitant", char['hesitant'])
        # level_headed
        r.set(f"{prefix}:level_headed", char['level_headed'])
        # quick
        r.set(f"{prefix}:quick", char['quick'])
        # tactician
        r.set(f"{prefix}:tactician", char['tactician'])
        # Ordinal
        r.set(f"{prefix}:ordinal", str(i))
        # Active
        r.set(f"{prefix}:active", char['active'])
        
        # Cards
        ## Hand
        r.delete(f"{prefix}:cards:hand")
        for card in char['cards']['hand']:
            r.sadd(f"{prefix}:cards:hand", card)
        ## Tactician
        r.delete(f"{prefix}:cards:tactician")
        for card in char['cards']['tactician']:
            r.sadd(f"{prefix}:cards:tactician", card)
    
    # SET DECK
    r.delete(f"{truncID}:deck")
    for ind, card in enumerate(init.State()['deck']['cards']):
        pair = { f'{card}': ind }
        r.zadd(f"{truncID}:deck", pair)
    
    r.set(f"{truncID}:deck:nextindex", init.State()['deck']['nextindex'])
    # SET ROUND
    r.set(f"{truncID}:round", init.State()['round'])

    # SET NEEDSHUFFLE
    r.set(f"{truncID}:deck:need_shuffle", init.State()['needshuffle'])
    return

@app.route('/tables/create', methods=['GET', 'POST'])
def createTable():
    # newTableID = str(uuid.uuid4())
    newTableID = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    if 'user' not in session:
        return

    user = session['user']

    if request.method == 'GET':
        # return redirect(url_for("index"))
        print('GETTING CREATE TABLE')
    else:
        print('POSTING CREATE TABLE')
        party = request.get_json()['party']
        # print(party)

        initParty = BuildParty(party)
        init = Initiative(initParty)
        init.Start()
        # r.set(newTableID, str(party))
        # Add Party to Redis cache under key of newTableID
        truncID = newTableID[-6:]
        # print(init.State()['party'])
        # SET PARTY
        r.set(f"{truncID}:owner", user)
        for i, char in enumerate(init.State()['party']):
            r.sadd(f"{truncID}:party", char['name'])

            prefix = f"{truncID}:{char['name']}"
            # hesitant
            r.set(f"{prefix}:hesitant", char['hesitant'])
            # level_headed
            r.set(f"{prefix}:level_headed", char['level_headed'])
            # quick
            r.set(f"{prefix}:quick", char['quick'])
            # tactician
            r.set(f"{prefix}:tactician", char['tactician'])
            # Ordinal
            r.set(f"{prefix}:ordinal", str(i))
            # Active
            r.set(f"{prefix}:active", char['active'])
            
            # PORTRAIT
            # Icon
            r.set(f"{prefix}:icon", char['icon'])
            # Color
            r.set(f"{prefix}:color", char['color'])

            # Cards
            ## Hand
            for card in char['cards']['hand']:
                r.sadd(f"{prefix}:cards:hand", card)
            ## Tactician
            for card in char['cards']['tactician']:
                r.sadd(f"{prefix}:cards:tactician", card)
        # SET DECK
        for ind, card in enumerate(init.State()['deck']['cards']):
            pair = { f'{card}': ind }
            r.zadd(f"{truncID}:deck", pair)
        r.set(f"{truncID}:deck:nextindex", init.State()['deck']['nextindex'])
        # SET ROUND
        r.set(f"{truncID}:round", init.State()['round'])
        # SET INDEX
        r.set(f"{truncID}:round:index", 0)

        # SET NEEDSHUFFLE
        r.set(f"{truncID}:deck:need_shuffle", init.State()['needshuffle'])

    return newTableID

def FetchPartyByID(id):
    partySet = r.smembers(f"{id[-6:]}:party")
    # print(partySet)
    if not partySet:
        return None

    parsedParty = []
    for member in partySet:
        prefix = f"{id[-6:]}:{member}"
        char = {
            'name': member,
            'hesitant': int(r.get(f"{prefix}:hesitant")),
            'quick': int(r.get(f"{prefix}:quick")),
            'level_headed': int(r.get(f"{prefix}:level_headed")),
            'tactician': int(r.get(f"{prefix}:tactician")),
            'ordinal': int(r.get(f"{prefix}:ordinal")),
            'active': int(r.get(f"{prefix}:active")),
            'icon': r.get(f"{prefix}:icon"),
            'color': r.get(f"{prefix}:color")
        }
        cards = {
            'hand': [card for card in r.smembers(f"{prefix}:cards:hand")],
            'tactician': [card for card in r.smembers(f"{prefix}:cards:tactician")]
        }
        char['cards'] = cards
        parsedParty.append(char)

    orderedParty = sorted(parsedParty, key=lambda x: x['ordinal'])
    builtParty = BuildParty(orderedParty)
    # print([(char['name'], char['cards']['hand']) for char in orderedParty])
    return builtParty

def FetchDeckByID(id):
    cards = [card for card in r.zrange(f"{id[-6:]}:deck", 0, -1)]
    nextindex = r.get(f"{id[-6:]}:deck:nextindex")
    needshuffle = r.get(f"{id[-6:]}:deck:needshuffle")

    deck = {
        'cards': cards,
        'nextindex': nextindex,
        'needshuffle': needshuffle
    }

    return deck

def FetchRoundByID(id):
    rd = r.get(f"{id[-6:]}:round")
    return rd

def FetchIndexByID(id):
    ind = r.get(f"{id[-6:]}:round:index")
    return int(ind)

def SetRedisActiveIndex(id, ind):
    r.set(f"{id[-6:]}:round:index", ind)
    return

@app.route('/redis/index/increment/<id>')
def IncrementIndex(id):
    ind = FetchIndexByID(id) + 1
    SetRedisActiveIndex(id, ind)
    response = {
        'index': ind
    }
    return jsonify(response) 

@app.route('/initiative/<id>/json/<rd>')
def jsonInitiative(id, rd):
    redisRound = FetchRoundByID(id)
    ind = FetchIndexByID(id)
    # SetRedisActiveIndex(id, ind)
    # print(f"The type of rd is {type(rd)}")
    # print(f"The type of redisRound is {type(redisRound)}")
    # print(f"fetching round {rd}; last round in Redis: {redisRound}")
    if int(rd) > int(FetchRoundByID(id)):
        UpdateRedisInitiative(id)
        SetRedisActiveIndex(id, 0)
        ind = 0

    fetchID = id[-6:]
    party = FetchPartyByID(fetchID)
    deck = FetchDeckByID(fetchID)
    round = int(FetchRoundByID(fetchID))
    initiative = Initiative(
        party,
        Deck(deck['cards'], int(deck['nextindex'])),
        round,
        deck['needshuffle']
    )

    state = initiative.State()
    for char in state['party']:
        char['active'] = 0
    state['party'][ind]['active'] = 1
    
    # print(ind)
    # print([(character['name'], character['active']) for character in initiative.State()['party']])

    # print(state)
    return jsonify(state)

@app.route('/tables/gm/<id>')
def gmTable(id):
    print('getting gm table...')
    if 'user' not in session:
        return redirect(url_for('index'))
    
    tableOwner = r.get(f"{id[-6:]}:owner")
    if tableOwner != session['user']:
        return redirect(url_for('index'))

    return render_template("gm_table.html", gameid=id)

@app.route('/tables/check/<id>')
def checkID(id):
    print(f'checking id: {id}' )
    if FetchRoundByID(id[-6:]) is not None:
        print('found active game')
        fetchedParty = FetchPartyByID(id)
        party = [char.name for char in fetchedParty]
        status = 'ok'
    else:
        print('no active game')
        party = 'none'
        status = 'error'
    response = {
        'status': status,
        'party': party
    }
    return jsonify(response)

@app.route('/tables/givecard', methods=['POST'])
def giveCard():
    req = request.get_json()
    # print("GIVE CARD REQUEST:")
    # print(req)

    c1 = req['origin']
    c2 = req['destination']
    card = req['card']
    id = req['id']

    r.srem(f"{id[-6:]}:{c1['name']}:cards:tactician", card)
    r.sadd(f"{id[-6:]}:{c2['name']}:cards:hand", card)

    UpdateRedisInitiative(id, False)

    return 'ok'

@app.route('/tables/join/<id>/<charname>')
def joinTable(id, charname):
    # print(id)
    ind = int(FetchIndexByID(id))
    return render_template("player_table.html", gameid=id, currentIndex=ind, charname=charname)

@socketio.on('join')
def handle_join(data):
    print('joining...')
    # if 'user' not in session:
    #     return
    # username = session['user']
    # queriedUser = m.User.query.filter(m.User.username == username).first()
    # userObject = m.userToDict(queriedUser)
    print(data)
    room = data['room']
    if 'user' not in session:
        return

    username = session['user']

    for existingRoom in rooms(request.sid):
        leave_room(existingRoom)

    if room not in rooms(request.sid):
        join_room(room)

    print(rooms(request.sid))

    print(f'{username} has entered room {room}.')
    # emit('message to room', {'message': '{} has joined.'.format(username), 'user': "SYS"}, room=room)
    return

# @socketio.on('message in room')
# def handle_message(data):
#     print(data)
#     username = data['username']
#     # queriedUser = m.User.query.filter(m.User.username == username).first()
#     queriedUser = None
#     room = data['room']
#     emit('message to room', { 'message': data['message'], 'user':queriedUser.displayname }, room=room)
#     return

@socketio.on('leave')
def handle_leave(data):
    print('leaving...')
    print(data)
    # leave room with id = data['room']
    # remove username (or displayname) from list of active players in room
    # if no users remain, destroy room
    if 'user' not in session:
        return

    username = session['user']
    # queriedUser = m.User.query.filter(m.User.username == username).first()

    room = data['room']
    leave_room(room)
    print(f'{username} has left room {room}')
    # emit('message to room', {'message': '{} has left room {}'.format(username, room), 'user': ""}, room=room)
    return

@socketio.on('start initiative in room')
def handle_initiative_start(data):
    emit('start initiative', room=data['room'])
    return

# @socketio.on('next')
# def handle_next(data):
#     # if data has new party list (new round), then display new round
#     # if not, advance the active element to next
    
#     # queryTable = m.Gametable.query.filter(m.Gametable.id == data['id']).first()
#     queryTable = None
#     # tableObject = m.tableToDict(queryTable)
#     # print(tableObject)
#     party = queryTable.characters
#     partyObject = [m.charToDict(character) for character in party]
#     print(partyObject)
#     initParty = BuildParty(partyObject)

#     initiative = Initiative(initParty)
#     initiative.NextRound()

#     state = initiative.State()

#     # return render_template("table_initiative.html", party=state['party'], round=state['round'], initiative=state)
#     packet = {
#         'initiative': state,
#         'round': state['round'],
#         'party': state['party']
#     }
#     emit('next round', packet, room=data['room'])
#     return

@socketio.on('update view')
def handle_update(data):
    emit('update', data, broadcast=True)
    return

@socketio.on('advance round')
def handle_advance(index):
    emit('advance', index, broadcast=True)
    return

@socketio.on("refresh view")
def handle_refresh():
    emit("refresh", broadcast=True)
    return

if __name__ == "__main__":
    # app.run()
    socketio.run(app)