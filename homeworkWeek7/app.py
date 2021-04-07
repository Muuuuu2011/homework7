from flask import Flask,redirect,request,render_template,session
import mysql.connector
import json
app=Flask(__name__)
app.config['SECRET_KEY'] = 'abc654_@123dda'

mydb = mysql.connector.connect(
  host="localhost",
  user="admin",
  password="1234",
  database="website"
)

mycursor = mydb.cursor()
#一開始的做法
# mycursor.execute("SELECT username FROM user")
# myusername = mycursor.fetchall()
# mycursor.execute("SELECT password FROM user")
# mypassword = mycursor.fetchall()

# print(myusername)
# print(mypassword)

# for y in mypassword:
#     continue

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup",methods=["POST"])
def signup():
    name = request.form["signupName"]
    username = request.form["signupUsername"]
    password = request.form["signupPassword"]
    mycursor.execute("SELECT username FROM user WHERE username=(%s)",(username,))
    check_Username = mycursor.fetchone()
    if check_Username != None:
      return redirect("/error?message=帳號已被註冊")
    # 原本的寫法
    # for x in myusername:
    #   if username in x:
    #     return redirect("/error")
    else:
      sql = "INSERT INTO user (name,username,password) VALUES (%s,%s,%s)"
      val = (name,username,password)
      mycursor.execute(sql, val)
      mydb.commit()
        #另一種方式
        # mycursor.execute("INSERT INTO 'user'('id','name','username','password','time') VALUES (%s,%s,%s,%s,%s)",(0,name,username,password,0))
        # mydb.commit()
      return redirect("/")
    
@app.route("/error")
def error():
  message = request.args.get("message")
  return render_template("error.html",name=message)


@app.route("/signin",methods=["POST"])
def signin():
  username = request.form["username"]
  password = request.form["password"]
  mycursor.execute("SELECT id,username FROM user WHERE username=(%s) and password=(%s)",(username,password,))
  check_MyAccount = mycursor.fetchone()
  if check_MyAccount != None:
    session["username"]= username
    session["id"]=check_MyAccount[0]
    return redirect("/member")
  else:
    return redirect("/error?message=帳號或密碼輸入錯誤")


@app.route("/member")
def member():
    if session.get('username') !=None :#原本用法session['username'] ：但如果內容不存在，將會報異常
      #所以改session.get('username') ：如果內容不存在，將返回None
      mycursor.execute("SELECT name FROM user WHERE username=(%s)",(session["username"],))
      check_MyName = mycursor.fetchone()
      name = check_MyName[0]
      return render_template("member.html",name=name,)  
    elif session.get('username') == None:
      return redirect("/")


@app.route("/api/users")
def users():
    if session["username"] != None:
        username = request.args.get("username")
        mycursor.execute("SELECT * FROM user WHERE username=(%s)",(username,))
        check_MyName = mycursor.fetchone()
        if check_MyName != None:
            result={
                "data":{
                    "id":check_MyName[0],
                    "name":check_MyName[1],
                    "username":check_MyName[2]
            }}
            return json.dumps(result,ensure_ascii=False)#可顯示中文字
        else:
            result={
                "data":check_MyName      
            }
            return json.dumps(result)
    else:
        return redirect("/")

@app.route("/api/user",methods=["POST"])
def user():
  if session["username"] != None:
    name = request.get_json()["name"]#html請求為json格式，所以要從request.args.get()改成request.get_json()["name"]
    mycursor.execute("UPDATE user SET name = %s WHERE id = %s",(name,session["id"]))
    mydb.commit()
    try:
      result={"ok":True}
      return json.dumps(result)
    except:
     result={"error":True}
     return json.dumps(result)
      
  else:
    return redirect("/")



@app.route("/signout")
def signout():
  session['username'] = None
  return redirect("/")


app.run(port=3000)


