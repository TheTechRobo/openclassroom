#THIS FILE IS TEMPORARY
from flask import Flask, render_template, request

app = Flask(__name__)

style_used = "style.css"

@app.route("/")
def welcome():
    return render_template('dash.html',mode="dark") #for testing

@app.route("/sitemap")
def nav():
    return render_template("generalNavBar.html",mode="light")
@app.route("/sitemap.xml")
def sitemap():
    return render_template("generalNavBar.html",mode="light")
@app.route("/notifs")
def notifications():
    return render_template("notifs.html")

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
