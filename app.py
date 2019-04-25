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
# I = Initiative(BuildParty(party))
# I.Start()

# tables = []

dbdict = {
    # 'sessionID': { 'username': uname, 'party': [<characters>] }
    'e172f1e1-0386-4b98-bf48-80df84573635': {'username': 'parkernalch', 'party': party, 'tables': [] },
    'tables': {
        # 'tableID': Initiative
    }
}

@app.route('/', methods=['GET', 'POST'])
@app.route('/party', methods=['GET', 'POST'])
def home():
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
        return render_template('layout.html', party=party, sessionID=sessionID)
    else:
        return redirect(url_for('cookie'))

@app.route('/<id>/party/add', methods=['POST'])
def AddPartyMember(id):
    party = dbdict[id]['party']
    request_data = request.get_json()
    print('dict entry')
    print(dbdict[id])
    print('party')
    for member in party:
        print(member.name)
    print('request_data')
    print(request_data)

    party = AddMemberTOParty(request_data, party)

    dbdict[id]['party'] = party
    print(dbdict[id])
    # receives a JSON character object
    # adds character to table <id>
    # returns a JSON party object for table <id>
    party = [character.Get() for character in party]
    response = jsonify(party)
    return response

@app.route('/<id>/party', methods=['GET'])
def GetParty(id):
    party = dbdict[id]['party']
    # returns a JSON party object for table <id>
    return jsonify([member.Get() for member in party])

@app.route('/<id>/party/<name>', methods=['GET'])
def GetPartyMember(id, name):
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
    if id not in dbdict.keys():
        print('id not in dictionary')
        return
    
    newchar = request.get_json()

    for character in dbdict[id]['party']:
        if character.name.replace(' ','-').lower() == name:
            character.name = newchar['name']
            character.tactician = newchar['tactician']
            character.level_headed = newchar['level_headed']
            character.quick = newchar['quick']
            character.hesitant = newchar['hesitant']
            return jsonify(character.Get())
    
    newparty = AddMemberTOParty(newchar, dbdict[id]['party'])
    print(newparty)
    return jsonify([character.Get() for character in newparty])

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

@app.route('/initiative/next', methods=['GET'])
def next_round():
    sessionID = request.cookies.get('InitiativeSession')
    if 'initiative' not in dbdict[sessionID].keys():
        return redirect(url_for('initiative'))

    initiative = dbdict[sessionID]['initiative']
    initiative.NextRound(deck=initiative.deck, round=initiative.round)
    return dbdict[sessionID]['initiative'].State()  


# @app.route('/table/<id>', methods=['GET'])
# def JoinTable(id):
#     # renders player-side initiative page
#     return

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
        return tableID
    return jsonify([key for key in dbdict['tables'].keys()])

if __name__ == "__main__":
    app.run()


# ====================
# Fill out form
# On submit, party member is added to list on right
# When finished, should go to initiative 
# probably needs a way to add people mid-initiative

# ===== Structure =======
#  ./ [GET]
    #  Goes to the home page with empty party and empty form

#  ./ [POST]
    # api POST page that takes in a new party member via JSON
    # and appends it to the existing party 

#  ./start [POST]
    # api POST page that takes in the party and starts initiative
    # Creates ID for the table
    # Redirects to /tables/<ID> as a [GET]

#  ./tables/<ID> [GET]
    # api GET page that 