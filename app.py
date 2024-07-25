from flask import Flask, render_template,request,redirect,url_for, jsonify
from flask import session as login_session
import pyrebase

app = Flask(__name__, template_folder='templates', static_folder="static")
app.config['SECRET_KEY'] = "amir"



firebaseConfig = {
  "apiKey": "AIzaSyBwE4yBk2KhZXkgr63augSbiLhQPcOvVTE",
  "authDomain": "memebakery-60b27.firebaseapp.com",
  "projectId": "memebakery-60b27",
  "storageBucket": "memebakery-60b27.appspot.com",
  "messagingSenderId": "935648374369",
  "appId": "1:935648374369:web:0aeb7c9a3b2f7698f48420",
  "measurementId": "G-RJHXTTTK25",
  "databaseURL":"https://memebakery-60b27-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
  if request.method == "GET":
    return render_template('signup.html')
  else :
    try:
      email = request.form['email']
      user_name = request.form['user_name'] 
      password = request.form['password']

      login_session['email'] = email
      login_session['password'] = password

      login_session['user'] = auth.create_user_with_email_and_password(email, password)
      user_id = login_session['user']['localId']
      user = {
        "email" : email,
        "password":password,
        "user_name":user_name
      }
      db.child('Users').child(user_id).set(user)

      return redirect(url_for('main'))
    except Exception as e:
      return render_template('error.html', e = e )

@app.route('/login', methods = ['GET', 'POST'])
def login():
  if request.method == "GET":
    return render_template('login.html')
  else :
    try :
      email = request.form['email'] 
      password = request.form['password']

      login_session['user'] = auth.sign_in_with_email_and_password(email, password)

      return redirect(url_for('main'))
    except Exception as e:
      return render_template('error.html', e = e)

@app.route("/memeKitchen", methods = ["GET", "POST"])
def memeKitchen():
  if "user" in login_session and login_session["user"] is not None:
    if request.method == "GET":
      return render_template('memeKitchen.html')
    else:
      if 'image' not in request.files:
        return redirect(request.url)

      image_file = request.files['image']
      if image_file.filename == '':
        return redirect(request.url)

      allowed_extensions = ['png', 'jpg', 'jpeg']
      if not image_file.filename.split('.')[-1].lower() in allowed_extensions:
          return redirect(request.url)

      user_id = login_session['user']['localId']

      image_path = f"{user_id}"

      storage.child(image_path).put(image_file.stream)

      login_session["image_url"] = storage.child(image_path).get_url(token='')  # Replace with authentication token if needed

      # print(login_session["image_url"])
      login_session["description"] = request.form['description']

      login_session['img_data'] = {
      'url': login_session["image_url"],
      'description' : login_session["description"]
      }

      db.child('Posts').push(login_session['img_data'])
      # return jsonify({'message': 'Image uploaded successfully!'})
      return redirect(url_for('memeBakery'))

    return redirect(request.url)
  else:
    return redirect(url_for('signup'))  

@app.route('/', methods = ['GET', 'POST'])
def main():
  if request.method == "POST":
    login_session['user'] =  None
    auth.current_user = None

  if "user" in login_session and login_session["user"] is not None:
    id = login_session['user']["localId"]
    user_name = db.child("Users").child(id).get().val()["user_name"]
  else:
    user_name = ""
  return render_template('index.html', user_name=user_name, active_user= "user" in login_session and login_session["user"] is not None)
    

@app.route('/memeBakery', methods = ['GET', 'POST'])
def memeBakery():
  if "user" in login_session and login_session["user"] is not None:
    if request.method == "GET":
      return render_template('memeBakery.html', img = login_session["image_url"], description = login_session["description"] , active_user= "user" in login_session and login_session["user"] is not None)
  else:
    return redirect(url_for('signup'))
  

@app.route('/allMemesPlace', methods = ['GET', 'POST'])
def allMemesPlace():
  if "user" in login_session and login_session["user"] is not None:
    if request.method == "GET":
      all_memes = db.child('Posts').get().val()
      return render_template('allMemesPlace.html', all_memes = all_memes, active_user= "user" in login_session and login_session["user"] is not None)
  else:
    return redirect(url_for('signup'))

if __name__ == '__main__':
    app.run(debug=True)

#   if login_session['user'] != None :
#  active_user = True