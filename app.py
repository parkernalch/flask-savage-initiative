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
    'e172f1e1-0386-4b98-bf48-80df84573635': {'username': 'parkernalch', 'party': party }
    # 'tables': { 'tableID': Initiative }
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
        return
    
    newchar = request.get_json()
    print(newchar)
    # jsonFormat = {
    #     oldchar: oldcharname,
    #     newchar: {
    #         name: name,
    #         tactician: tactician,
    #         level_headed: level_headed,
    #         quick: quick,
    #         hesitant: hesitant
    #     }
    # }

    for character in dbdict[id]['party']:
        if character.name.replace(' ','-').lower() == name:
            character.name = newchar['name']
            character.tactician = newchar['tactician']
            character.level_headed = newchar['level_headed']
            character.quick = newchar['quick']
            character.hesitant = newchar['hesitant']
            return jsonify(character.Get())
    return "No Character Found with the name {}".format(name)

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


# @app.route('/initiative', methods=['POST', 'GET'])
# def initiative():
#     sessionID = request.cookies.get('InitiativeSession')
#     if not sessionID:
#         return redirect(url_for('set_cookie'))

#     session = dbdict[sessionID]

#     req_data = request.get_json()

#     if 'party' in req_data.keys():
#         party = req_data['party']
#         print(party)
#         return jsonify(Initiative(BuildParty(party)).Start())

#     #print(party)
#     #return jsonify(Initiative(party))
#     return 'No Data'

# @app.route('/initiative/next', methods=['POST'])
# def next_round():
#     req_data = request.get_json()
    
#     party = None
#     if 'party' in req_data.keys():
#         party = BuildParty(req_data['party'])

#     deck = None
#     if 'deck' in req_data.keys():
#         deck = req_data['deck']
#         print(deck)
#         # cards = req_data['deck']['cards']
#         # nextcard = req_data['deck']['nextCard']

#     if 'round' in req_data.keys():
#         round = req_data['round']

#     Init = Initiative(party)
#     return jsonify(Init.NextRound(deck=deck, round=round))    


@app.route('/table/<id>', methods=['GET'])
def JoinTable(id):
    # renders player-side initiative page
    return

@app.route('/table/<id>/gamemaster', methods=['GET'])
def RunTable(id):
    # renders gm-side initiative page
    return

@app.route('/tables/create', methods=['POST'])
def CreateTable():
    # receives posted complete party
    # creates a unique ID (probably needs a DB now)
    # renders the '/table/<id>/gamemaster' link
    return

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