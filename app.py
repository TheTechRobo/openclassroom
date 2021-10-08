from flask import *
from rethinkdb import r
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

if __name__ == '__main__':
    app.run()
