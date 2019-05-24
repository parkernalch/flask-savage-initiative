import flask
from cards import *
from flask import request, jsonify, render_template, redirect, url_for, session, g
import uuid
from os import urandom
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import SocketIO, join_room, leave_room, send, emit, rooms
from flask_sqlalchemy import SQLAlchemy
import models as m
import json

app  = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mHCbBr0EbK:r5BX9RsjWu@remotemysql.com:3306/mHCbBr0EbK'
db = SQLAlchemy(app)
socketio = SocketIO(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    req_data = request.get_json()
    # POST
    # check hashed password against pw database
    # reroute to current page
    if request.method == 'POST':
        uname = req_data['username']
        pwd = req_data['password']
        user = m.User.query.filter(m.User.username == uname).first()

        if check_password_hash(user.password, pwd):
            user.authenticated = True
            session['user'] = user.username
            # return '{} successfully logged in as {}'.format(user.displayname, user.username)
            responseUser = {'displayname': user.displayname, 'username': user.username }
            return jsonify(responseUser)
        return 'login failed'

    # GET
    # display login screen
    return render_template("login.html")

@app.route('/logout', methods=['POST'])
def logout():
    print('starting logout')
    req_data = request.get_json()
    # uname = req_data['username']
    session.pop('user', None)
    return '{} successfully logged out'.format(req_data['username'])

@app.route('/', methods=['GET'])
def index():
    # check if logged in
    user = None
    if 'user' in session:
        print('user in session')
        queriedUser = m.User.query.filter(m.User.username == session['user']).first()
        user = queriedUser.displayname
    # display homepage
    print('user not in session')
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
        encounter = session['encounter']
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
    # print(initParty)

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

@app.route('/tables', methods=['GET', 'POST'])
def tables():
    # POST
    # Can only get to tables if signed in
    if 'user' not in session:
        return redirect(url_for('home'))
    user = session['user'] # username
    queriedUser = m.User.query.filter(m.User.username == user).first()
    
    ownedTableQuery = m.Gametable.query.filter(m.Gametable.gamemaster_id == queriedUser.id)
    ownedTables = [{'id': table.id, 'name': table.name, 'description': table.description } for table in ownedTableQuery]

    joinedTableQuery = m.Gametable.query.all()
    # print(joinedTableQuery)
    joinedTables = [{'id': table.id, 'name': table.name, 'description': table.description } for table in joinedTableQuery]
    # print(joinedTables)
    if request.method == 'POST':
        req_data = request.get_json()
        # request data in the form:
        # req_data = {
        # 'table-name': tablename,
        # 'party': party (from encounter),
        # 'table-description': description
        # }
        # create new table
        # display list of tables
        return render_template("tables.html", tables=ownedTables, joinedtables=joinedTables)

    # GET
    # display list of available tables
    return render_template("tables.html", tables=ownedTables, joinedtables=joinedTables)

@app.route('/tables/<id>/gm')
def gm_table(id):
    print(id)
    queryTable = m.Gametable.query.filter(m.Gametable.id == id).first()
    tableObject = m.tableToDict(queryTable)

    return render_template('table.html', table=tableObject, user=session['user'])

@app.route('/tables/<id>/player')
def player_table(id):
    print(id)
    queryTable = m.Gametable.query.filter(m.Gametable.id == id).first()
    tableObject = m.tableToDict(queryTable)

    return render_template('table.html', table=tableObject, user=session['user'])

@app.route('/tables/<id>/initiative', methods=['GET'])
def tableInitiative(id):
    queryTable = m.Gametable.query.filter(m.Gametable.id == id).first()
    tableObject = m.tableToDict(queryTable)
    # print(tableObject)
    party = queryTable.characters
    partyObject = [m.charToDict(character) for character in party]
    print(partyObject)
    initParty = BuildParty(partyObject)

    initiative = Initiative(initParty)
    initiative.Start()

    state = initiative.State()

    # return render_template("initiative.html", party=state['party'], round=state['round'], initiative=state)
    return render_template("table_initiative.html", party=state['party'], round=state['round'], initiative=state)

@socketio.on('join')
def handle_join(data):
    if 'user' not in session:
        return
    username = session['user']
    queriedUser = m.User.query.filter(m.User.username == username).first()
    # userObject = m.userToDict(queriedUser)

    room = data['room']
    if room not in rooms():
        join_room(room)

    print(username + ' has entered room {} as {}.'.format(room, queriedUser.displayname))
    emit('message to room', {'message': '{} has joined as {}'.format(username, queriedUser.displayname), 'user': ""}, room=room)
    return

@socketio.on('message in room')
def handle_message(data):
    print(data)
    username = data['username']
    queriedUser = m.User.query.filter(m.User.username == username).first()

    room = data['room']
    emit('message to room', { 'message': data['message'], 'user':queriedUser.displayname }, room=room)
    return

@socketio.on('leave')
def handle_leave(data):
    print('leaving...')
    print(data)
    # leave room with id = data['room']
    # remove username (or displayname) from list of active players in room
    # if no users remain, destroy room
    username = data['username']
    # queriedUser = m.User.query.filter(m.User.username == username).first()

    room = data['room']
    leave_room(room)
    print(username + ' has left room {}'.format(room))
    emit('message to room', {'message': '{} has left room {}'.format(username, room), 'user': ""}, room=room)
    return

@socketio.on('start initiative in room')
def handle_initiative_start(data):
    emit('start initiative', room=data['room'])
    return

@socketio.on('next')
def handle_next(data):
    # if data has new party list (new round), then display new round
    # if not, advance the active element to next
    return

@socketio.on('update player view')
def handle_update(data):
    # data should contain some key that I can use to indicate which type of change
    # - Wound
    # - Shaken
    # - Dazed
    # - etc.
    # Update the player view accordingly
    return

@app.route('/vault', methods=['GET', 'POST'])
def vault():
    # POST
    # take character object and write to localstorage
    # display list of available characters
    # GET
    # display list of available characters
    return None




# @app.route('/initiative', methods=['GET'])
# def initiative():
#     sessionID = request.cookies.get('InitiativeSession')
#     if not sessionID:
#         return redirect(url_for('set_cookie'))

#     party = dbdict[sessionID]['party']
#     dbdict[sessionID]['initiative'] = Initiative(BuildParty(party))
#     dbdict[sessionID]['initiative'].Start()
#     # req_data = request.get_json()
#     return dbdict[sessionID]['initiative'].State() 


# @app.route('/table/<id>', methods=['GET'])
# def JoinTable(id):
#     # renders player-side initiative page
#     # print('starting /table/<id> for id={}'.format(id))
#     if id not in dbdict['tables'].keys():
#         return redirect(url_for('tables'))
#     dbdict['tables'][id]['initiative'].Start()
#     table = dbdict['tables'][id]
#     party = table['initiative'].party
#     round = table['initiative'].round
#     # return render_template("initiative.html", party=party, sessionID="", tableID=id, round=round)
#     return render_template('table.html', party=party, tableid=id, round=round, table=table)

# @app.route('/table/<id>/initiative', methods=['POST'])
# def StartInitiative(id):
#     party = dbdict['tables'][id]['initiative'].party
#     tableid = id
#     round = dbdict['tables'][id]['initiative'].round
#     return render_template("initiative.html", party=party, tableid=id, round=round)

# @app.route('/table/<id>/next', methods=['GET'])
# def next_round(id):
#     if id not in dbdict['tables'].keys():
#         return redirect(url_for('tables'))

#     round = dbdict['tables'][id]['initiative'].round
#     if round == 0:
#         return redirect(url_for('JoinTable'))

#     round += 1
#     initiative = dbdict['tables'][id]['initiative']
#     dbdict['tables'][id]['initiative'].NextRound()
#     party = dbdict['tables'][id]['initiative'].party
#     return render_template("initiative.html", party=party, sessionID="", tableID=id, round=round)

# @socketio.on('next round')
# def handle_next_round(data):
#     print('Going to next round in room {}'.format(data['room']))
#     # print(emit('go to next', room=data['room']))
#     emit('go to next', party=data['party'], room=data['room'])

# @socketio.on('join')
# def handle_join_event(data):
#     username = data['username']
#     room = data['room']
#     join_room(room)
#     print(username + ' has entered room {}'.format(room))
#     # send(username + ' has entered the room.', room=room, callback=ack)

# @socketio.on('leave')
# def handle_leave_event(data):
#     username = data['username']
#     room = data['room']
#     leave_room(room)
#     print(username + ' has left room {}'.format(room))
#     # send(username + ' has left the room.', room=room, callback=ack)

# @socketio.on('start initiative in room')
# def handle_initiative_start(data):
#     emit('start initiative', room=data['room'])

# @app.route('/tables', methods=['GET', 'POST'])
# def tables():
#     if request.method == 'POST':
#         tableID = str(uuid.uuid4())
#         while tableID in dbdict['tables'].keys():
#             tableID = str(uuid.uuid4())
#         dbdict['tables'][tableID] = {
#             'initiative': None,
#             'name': 'new table',
#             'members': []
#         }

#     tables = [(id, table) for id, table in dbdict['tables'].items()]
#     return render_template("tables.html", tables=tables)

if __name__ == "__main__":
    # app.run()
    socketio.run(app)