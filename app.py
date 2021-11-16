from flask import *
import os
import flask
from rethinkdb import r
import rethinkdb
import werkzeug

r.set_loop_type('asyncio')
app = Flask(__name__)
app.secret_key = os.urandom(42)
style_used = "style.css"

# hi {{{
import flask_login
from flask_login import login_required

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class User(flask_login.UserMixin): pass
@login_manager.user_loader
async def user_loader(uname):
    conn = await r.connect("localhost",28015)
    gotuser = await r.db("openclassroom").table("userSettings").filter(r.row["user_stuff"] == uname).run(conn)
    async for gottuser in gotuser: pass #gets item from cursor
    if gottuser == gotuser: return #This means that there were no items in the cursor, as there was nothing to `for`. I've tried for's ELSE statement but that always ran for some reason :thinking:
    user = User()
    user.id = uname
    return user
@login_manager.request_loader
async def request_loader(request):
    uname = request.form.get('uname')
    conn = await r.connect("localhost",28015)
    gotuser = await r.db("openclassroom").table("userSettings").filter(r.row["user_stuff"] == uname).run(conn)
    async for gottuser in gotuser: pass #gets item from cursor
    if gottuser == gotuser: return
    user = User()
    user.id = uname
    return user

@login_required
@app.route("/post", methods=["POST"])
async def post():
    try:
        print(request.values['typee'], request.values["name"])
    except KeyError: abort(400)
    return request.values["typee"] + ";;" + request.values["name"]

@login_required
@app.route("/postAssignment")
async def postAssignment():
    return render_template('PostAssignment.html')

@app.route('/login', methods=['GET','POST'])
async def login():
    if flask.request.method == 'GET':
        return '''
    <FORM ACTION='/login' METHOD='POST'>
    <INPUT TYPE='TEXT' NAME='uname' ID='uname' PLACEHOLDER='username'/>
    <INPUT TYPE='password' NAME='password' ID='password' PLACEHOLDER='password'/>
    <input type='submit' name='submit'/>
    </FORM>
        '''
    uname = flask.request.form['uname']
    #print(werkzeug.security.generate_password_hash(flask.request.form['password'], salt_length=16))
    if werkzeug.security.check_password_hash(await GetPass(uname), flask.request.form['password']):
        user = User()
        user.id = uname
        flask_login.login_user(user)
        return 'Logged in'
    return 'Bad login'
async def GetPass(uname):
    conn = await r.connect("localhost",28015)
    user = uname
    userSettings = await r.db("openclassroom").table("userSettings").filter(r.row["user_stuff"] == user).run(conn)
    async for DEETA in userSettings: pass
    try: DEETA
    except UnboundLocalError: return ""
    if DEETA == userSettings: return "" #relies on disallowing blank passwords
    return DEETA['secret']
# }}}

@app.route("/")
async def welcome():
    conn = await r.connect("localhost", 28015)
    user = "test" #in the future, make this a session id with cookies
    userSettings = await r.db("openclassroom").table("userSettings").filter(r.row["user_stuff"] == user).run(conn)
    async for a in userSettings:
        userSettings = a
    print(userSettings)
    datums = {
            "mode": userSettings['mode'],
            "upcomingDueList": sorted({20210702: "dsdeI", 20210701: "sss"}.keys(), reverse=True),
            "pinned": [{"id": "JFJdu3", "name": "hi", "teach": "Joe Mama", "desc": "Your Class"}, {"id": "d", "name": "hi", "teach": "Joe Mama", "desc": "fj"}],
            "upcomingDue": {20210702: "dsdeI", 20210701: "sss"},
            "idToName": {"sss": "Sizzle", "dsdeI": "random letters assignment"}
        }
    return render_template('dash.html', **datums)
@app.route("/sitemap")
async def nav():
    return render_template("generalNavBar.html",mode="dark")
@app.route("/sitemap.xml")
async def sitemap():
    return render_template("generalNavBar.html",mode="dark")
@app.route("/notifs")
async def notifications():
    msg = [{"relativeurl":"goToNotif/hw","name":"Joe posted a new assignment: Mama","class":{"name":"d"}}, {"relativeurl":"goToNotif/hw","name":"Joe posted a new sssssssassignment: Mama","class":{"name":"CLASSNAME"}}]
    return render_template("notifs.html", lenMsg=len(msg), msg=msg)
@app.route("/DismissPin/<id>")
async def dismiss(id):
    print(f"Failed to dismiss {id}...")
    abort(418)
@app.route("/RerunSetup")
async def Setup():
    return "GO TO <a href='/RerunSetup/LoadDB'>LOADDB</a>"
    #return render_template("setup.html")
@app.route("/RerunSetup/LoadDB")
async def CreateDatabase():
    conn = await r.connect("localhost", 28015)
    try: await r.db_create("openclassroom").run(conn)
    except rethinkdb.errors.ReqlOpFailedError:
        #print("Except")
        print("There is already a database named openclassroom. Remove it before rerunning setup. In the future there will be an option to change the database name.")
        return "see output", 500
    await r.db("openclassroom").table_create("userSettings").run(conn)
    await r.db("openclassroom").table_create("assignments").run(conn)
    await r.db("openclassroom").table_create("classes").run(conn)
    await r.db("openclassroom").table("userSettings").insert(
            {"user_stuff": "test",
                "secret": werkzeug.security.generate_password_hash('pass', salt_length=16),
                "mode": "dark"}
            ).run(conn)
    return "Hello World! In the future there'll be more shit to configure."
@app.after_request
def add_header(r):#https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
#@app.errorhandler(TypeError)
@app.errorhandler(rethinkdb.errors.ReqlOpFailedError)
def typeerror_handler(e):
    return "Failed to load database! Make sure you have a database called `openclassroom' in rethinkdb, and that you did not remove any key elements. If all else fails, <a href='/RerunSetup?issue=databaseInaccessible'>rerun setup</a>.", 500
if __name__ == '__main__':
    app.run()
