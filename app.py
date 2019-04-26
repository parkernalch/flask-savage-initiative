import flask
from cards import *
from flask import request, jsonify, render_template, redirect, url_for
import uuid

app  = flask.Flask(__name__)
app.config['DEBUG'] = True


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
# I.Start()

# tables = []

dbdict = {
    # 'sessionID': { 'username': uname, 'party': [<characters>] }
    '82abd0e5-f588-4308-ae23-46fc394bb092': {'username': 'parkernalch', 'party': party, 'tables': [] },
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
    }
}

@app.route('/', methods=['GET', 'POST'])
def home():
    # print('routing party or /')
    sessionID = request.cookies.get('InitiativeSession')
    if not sessionID:
        return redirect(url_for('cookie'))

    if sessionID in dbdict.keys():
        session = dbdict[sessionID]
        if 'party' in session.keys():
            party = session['party']
        else:
            party = []
        # return render_template('home.html', party=party, sessionID=sessionID)
        return render_template('layout.html', party=party, sessionID=sessionID, tableID="")
    else:
        return redirect(url_for('cookie'))

@app.route('/party', methods=['GET'])
def party():
    # print('starting /party')
    sessionID = request.cookies.get('InitiativeSession')
    if not sessionID:
        return redirect(url_for('cookie'))
    if sessionID not in dbdict.keys():
        return redirect(url_for('cookie'))
    
    party = dbdict[sessionID]['party']
    # print('rendering party list: party={}, sessionID={}'.format([member.name for member in party], sessionID))
    return render_template('party_list.html', party=party, sessionID=sessionID, tableID="")

@app.route('/<id>/party/add', methods=['POST'])
def AddPartyMember(id):
    party = dbdict[id]['party']
    request_data = request.get_json()
    # print('dict entry')
    # print(dbdict[id])
    # print('party')
    # for member in party:
        # print(member.name)
    # print('request_data')
    # print(request_data)

    party = AddMemberTOParty(request_data, party)

    dbdict[id]['party'] = party
    # print(dbdict[id])
    # receives a JSON character object
    # adds character to table <id>
    # returns a JSON party object for table <id>
    party = [character.Get() for character in party]
    response = jsonify(party)
    # return response
    return redirect('/party')

# @app.route('/<id>/party', methods=['GET'])
# def GetParty(id):
#     party = dbdict[id]['party']
#     # returns a JSON party object for table <id>
#     return jsonify([member.Get() for member in party])

@app.route('/<id>/party/<name>', methods=['GET'])
def GetPartyMember(id, name):
    # print('starting GetPartyMember [get]: id={}, name={})'.format(id, name))
    member = {}
    # print(id)
    if id in dbdict.keys():
        # print(dbdict[id])
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
        response.set_cookie('InitiativeSession', sessionID)
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

# @app.route('/table/<id>/gamemaster', methods=['GET'])
# def RunTable(id):
#     # renders gm-side initiative page
#     return

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
    app.run()