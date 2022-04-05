import json
import os
from wsgiref.util import request_uri
from flask import Flask, flash, render_template , redirect, session, url_for , request
from flask_pymongo import PyMongo
from itsdangerous import exc
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/wad"
dirname = os.path.dirname(__file__)
filenamepath = os.path.join(dirname, '\res')
app.config['UPLOAD_FOLDER'] = filenamepath
app.secret_key = 'super67sEcret459!!key@s'
mongo = PyMongo(app)
print('---LOG: best debug method: WEBSITE: OK')


def authCheck():
    try:
        if session(['logged']):
            return True
        else:
            return False
    except:
        return False

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/stories')
def showStories():
    posts = list(mongo.db.stories.find({}))
    for post in posts:
        print(post['text'])
    return render_template('stories.html', posts = posts) 

@app.route('/postStory',methods= ['POST'])
def postStory():
    if authCheck:
        author = session['logged']
        story_text = request.form.get("story")
        story_data = {'author': author, 'text': story_text}
        mongo.db.stories.insert_one(story_data)
        print("--LOG Story uploaded!")
        return redirect(url_for('showStories'))

    else:
        flash("Error, you are not logged in!")
        return render_template("index.html")

@app.route('/signup',methods = ['POST', 'GET'])
def signup():
    session.clear()
    if request.method == 'POST':
      email = request.form['email']
      password = request.form['pass']

      email_found = mongo.db.users.find_one({"email": email})
      if(email_found):
          print("---LOG: memory loss!")
          #print user already exists message
          flash("User already exists!")
          return render_template("index.html")
      else:
        #create user inside mongo
        user_data = {'email': email, 'password': password}
        mongo.db.users.insert_one(user_data)
        print('---LOG: great success')
        flash("User created succesfully!")
        return render_template("index.html")
    else: #get method
      return render_template("signup.html")

@app.route('/auth',methods = ['POST', 'GET'])
def auth():
    session.clear()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        #auth check
        user = mongo.db.users.find_one({"email": email, "password": password})
        try:
            db_email=str(user.get('email'))
            db_password=str(user.get('password'))
            if(db_email==email and db_password==password):
                #login success
                flash("Welcome: "+email)
                session['logged'] = email
                return render_template("index.html")
            else:
                flash("Wrong username or password!", 'danger')
                return redirect(request.url)
        except Exception as e:
            print(e)
            flash("Wrong username or password!")
            return redirect(request.url)
    else: #get method
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out succesfully!")
    return render_template("index.html")

app.run(host='localhost', port=5000)