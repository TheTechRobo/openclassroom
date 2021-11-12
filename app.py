from flask import *
from rethinkdb import r
import rethinkdb
r.set_loop_type('asyncio')
app = Flask(__name__)

style_used = "style.css"

@app.route("/")
async def welcome():
    conn = await r.connect("localhost", 28015)
    user = "test_openclassroom_user" #in the future, make this a session id with cookies
    userSettings = await r.db("openclassroom").table("userSettings").filter(r.row["user_stuff"] == user).run(conn)
    async for i in userSettings:
        userSettings = i
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
    return render_template("setup.html")
@app.route("/RerunSetup/LoadDB")
async def CreateDatabase():
    conn = await r.connect("localhost", 28015)
    try: await r.db_create("openclassroom").run(conn)
    except:
        #print("Except")
        raise
        print("There is already a database named openclassroom. Remove it before rerunning setup. In the future there will be an option to change the database name.")
        return "see output", 500
    await r.db("openclassroom").table_create("userSettings").run(conn)
    await r.db("openclassroom").table_create("assignments").run(conn)
    await r.db("openclassroom").table_create("classes").run(conn)
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
@app.errorhandler(TypeError)
@app.errorhandler(rethinkdb.errors.ReqlOpFailedError)
def typeerror_handler(e):
    return "Failed to load database! Make sure you have a database called `openclassroom' in rethinkdb, and that you did not remove any key elements. If all else fails, <a href='/RerunSetup?issue=databaseInaccessible'>rerun setup</a>.", 500
if __name__ == '__main__':
    app.run()
