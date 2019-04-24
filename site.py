import flask
from cards import *
from flask import request, jsonify, render_template, redirect, url_for
import uuid

app  = flask.Flask(__name__)
app.config['DEBUG'] = True

dbdict = {
    'users': {
        # sessionID : { username: username, password: password}
        'e172f1e1-0386-4b98-bf48-80df84573635': {'username': 'Parker', 'party' = []}
    },
    'tables': {
        # tableid: { state: json_initiative_object, players: [<usernames>]}
    }
}

@app.route('/')
@app.route('/home')
def home():
    sessionID = request.cookies.get('InitiativeSession')
    print(sessionID)
    print(dbdict['users'])
    if sessionID:
        try:
            user = dbdict['users'][sessionID]
            return render_template('home.html', user=user['username'])
        except KeyError:
            print('No User Found!!')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        req_data = request.get_json()
        print(req_data)
        if not req_data:
            print('req_data is empty')
            return render_template('login.html')
        if 'user' in req_data.keys():
            user = req_data['user']
            
            found = False
            sessID = ''
            while not found:
                for session_id, stored_user in dbdict['users'].items():
                    if stored_user['username'] == user['username']:
                        found = True
                        sessID = session_id
                break
 
            if not found:
                sessID = str(uuid.uuid4())

            dbdict['users'][sessID] = user
            print(dbdict['users'])
        
        response = redirect(url_for("build"))
        response.set_cookie('InitiativeSession', sessID)
        return response
    return render_template('login.html')

@app.route('/build', methods=['GET', 'POST'])
def build():
    sessionID = request.cookies.get('InitiativeSession')
    print(sessionID)
    if sessionID in dbdict['users'].keys():
        user = dbdict['users'][sessionID]
        print('USER FOUND')
        uname = user['username']
        return redirect(url_for('home'))

    
    if sessionID:
        try:
            user = dbdict['users'][sessionID]
            return render_template('home.html', user=user['username'])
        except KeyError:
            print('no user found!')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/<id>/party/add', methods=['POST'])
def AddPartyMember(id):
    # receives a JSON character object
    # adds character to table <id>
    # returns a JSON party object for table <id>
    return

@app.route('/<id>/party', methods=['GET'])
def GetParty(id):
    # returns a JSON party object for table <id>
    return

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