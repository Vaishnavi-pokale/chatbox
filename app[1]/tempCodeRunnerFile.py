from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

# Connect to MySQL server
cnx = mysql.connector.connect(
    host="127.0.0.1",
    port="3306",
    user="root",
    password="password",
    database="python" )

#cursor object
cur = cnx.cursor()

#object of flask class
app = Flask(__name__)
app.secret_key = "shreya"



@app.route('/')
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user:
            return "Email already exists!"
        cur.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", (email, username, password))
        cnx.commit()
        return redirect('/login')  # Redirect to the login page after successful registration
    return render_template("register.html")  # Display the register form




#route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "email" in request.form and "password" in request.form:  
            email = request.form["email"]
            password = request.form["password"]

            cur.execute("SELECT id, username FROM users WHERE email = %s AND password = %s", (email, password))
            user = cur.fetchone()

            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect("/showusers")
            else:
                return "Invalid credentials!"
    return render_template("login.html")


#route for user list
@app.route("/showusers")
def showusers():
    cur.execute("SELECT id, username FROM users WHERE id != %s", (session['user_id'],))
    users = cur.fetchall()
    return render_template("showusers.html", users=users)

@app.route("/chat",methods=["GET", "POST"])
def chat():
    receiver_id = request.args['receiver_id']
    q = "SELECT users.username, chatbox.message FROM chatbox INNER JOIN users ON chatbox.sender_id = users.id WHERE reciever_id=%s AND sender_id=%s"
    cur.execute(q, (session['user_id'] , receiver_id))
    res = cur.fetchall()
    q = "SELECT  users.username, chatbox.message FROM chatbox INNER JOIN users ON chatbox.sender_id = users.id WHERE reciever_id=%s AND sender_id=%s" 
    cur.execute(q, (receiver_id, session['user_id']))
    res2 = cur.fetchall()
    return render_template('chat.html', receiver_id=receiver_id, res=res, res2=res2)

@app.route("/sendmsg", methods=['post'])
def sendmsg():
    receiver_id = request.form['receiver_id']
    msg = request.form['msg']
    sender_id = session['user_id']
    q = "INSERT INTO chatbox VALUES(null, %s, %s, %s)"
    cur.execute(q, (sender_id, receiver_id, msg))
    cnx.commit()
    return redirect(url_for('chat', receiver_id=receiver_id))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
