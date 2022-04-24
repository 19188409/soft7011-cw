from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'examplekey'


class vaccineAccountManager:
    def __init__(self, fname, sname, dob, gender, address, telephone, email, staff, job, crown):
        self.fname = fname
        self.sname = sname
        self.age = dob
        self.gender = gender
        self.address = address
        self.telephone = telephone
        self.email = email
        self.staffNumber = staff
        self.jobTitle = job
        self.crownpass = crown

    cluster = MongoClient(
        "mongodb+srv://admin:SOFT7011db@cluster0.0ojaw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = cluster["bookingdb"]
    collection = db["date"]
    user_db = cluster["vaccinedb"]
    user_collection = user_db["users"]

    # connection to the crowpass holder database, to update their status
    cp_cluster = MongoClient(
        "mongodb+srv://19179422:soft7011@cluster0.whl83.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    cp_db = cp_cluster['users']
    cp_col = cp_db['vacStatus']

    def return_cp_db(self, cp):
        print(cp)
        x = list(self.user_collection.find({"crownpassID": cp}))
        print(x)
        print(type(x))
        x = x[0]
        return x

    def record_vaccine(self, crown_number):
        x = list(self.cp_col.find({"crownpassID": crown_number}))
        x = x[0]
        vacStatus = x["vacStatus"]
        # get the vacStatus from the cp_db and update it
        if vacStatus == "No vaccination":
            self.user_collection.update_one(x, {"$set": {"vacStatus": "One dose"}})
        elif vacStatus == "One dose":
            self.user_collection.update_one(x, {"$set": {"vacStatus": "Two or more doses"}})

    def manage_user_update_details(self, crown_number, atrr_to_change, attribute_new):
        # each user has a unique staff number so it is easy to use this to find the entry in the database
        x = list(self.user_collection.find({"crownpassID": crown_number}))
        x = x[0]
        if atrr_to_change == "fname":
            self.user_collection.update_one(x, {"$set": {"firstName": attribute_new}})
            print("Database Updated")
        elif atrr_to_change == "sname":
            self.user_collection.update_one(x, {"$set": {"lastName": attribute_new}})
            print("Database Updated")
        elif atrr_to_change == "gender":
            self.user_collection.update_one(x, {"$set": {"gender": attribute_new}})
            print("Database Updated")
        elif atrr_to_change == "address":
            self.user_collection.update_one(x, {"$set": {"address": attribute_new}})
            print("Database Updated")
        elif atrr_to_change == "telephone":
            self.user_collection.update_one(x, {"$set": {"telephone": attribute_new}})
            print("Database Updated")
        elif atrr_to_change == "email":
            self.user_collection.update_one(x, {"$set": {"email": attribute_new}})
            print("Database Updated")
        elif atrr_to_change == "staff":
            self.user_collection.update_one(x, {"$set": {"staff": attribute_new}})
            print("Database Updated")
        elif atrr_to_change == "job":
            self.user_collection.update_one(x, {"$set": {"job": attribute_new}})
            print("Database Updated")

    def Convert(self, string):
        string = string.replace('[', '')
        string = string.replace(']', '')
        li = list(string.split(","))
        if not all(isinstance(x, (int, float)) for x in li):
            li = list(map(int, li))
            return li
        else:
            print("Error: the date/time format that Convert function has received are incorrect")
            return 0

    def get_date(self, date):
        x = list(self.collection.find({"date": date}))
        y = x[0]["time_slots"]
        y = self.Convert(y)
        z = x[0]["status"]
        z = self.Convert(z)
        date_list = [y, z]
        print("List from database:  ", date_list)
        return date_list

    def update_timeslots_db(self, old_doc, new_doc):
        self.collection.update_one({"date": old_doc}, {"$set": {"status": str(new_doc)}})
        print("Database Updated")

    def manage_bookings(self, date, time_slot, action):  # vaccines is a dictionary
        if action == "add":
            date = str(date)
            list = self.get_date(date)
            ind = list[0].index(time_slot)
            list[1][ind] = 1
            print("After adjustments: ", list[1])
            self.update_timeslots_db(date, list[1])

        elif action == "remove":
            date = str(date)
            list = self.get_date(date)
            ind = list[0].index(time_slot)
            list[1][ind] = 0
            print("After adjustments: ", list[1])
            self.update_timeslots_db(date, list[1])

        else:  # action is to update the booking status to completed
            # get the correct date list from the database
            date = str(date)
            list = self.get_date(date)
            ind = list[0].index(time_slot)
            list[1][ind] = 2
            print("After adjustments: ", list[1])
            self.update_timeslots_db(date, list[1])




@app.route("/", methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        username = request.form['username']
        staff = request.form['staff']
        password = request.form['password']
        ans, user_frm_db = authenticate_func(staff, username, password)
        if ans:
            session['data'] = user_frm_db
            session['user'] = username
            return redirect(url_for('homepage'))
    return render_template('dashboard.html')


@app.route("/account")
def account():
    return render_template('accountManager.html', name_string=session['user'], data=session['data'])


@app.route("/accountDetailEdit", methods=['GET', 'POST'])
def accountDetailEdit():
    user_session_data = session['data']
    print(user_session_data)
    cp = user_session_data['crownpassID']

    if request.method == "POST":
        print("Button was clicked")
        fname = request.form['fname']
        sname = request.form['lname']
        address = request.form['address']
        email = request.form['email']
        gender = request.form['gender']
        job = request.form['job']
        staff = request.form['staff']
        telephone = request.form['telephone']
        list = [fname, sname, address, email, gender, job, staff, telephone]

        account_manager_updater(cp, list)
        print("DB should be updated, user will need to re-login")
        return redirect('/')

    return render_template('accountDetailEdit.html', name_string=session['user'], data=session['data'])



@app.route("/homepage", methods=['GET', 'POST'])
def homepage():
    #return
    #if request.method == "POST":
    #    return redirect(url_for("account"))
    return render_template("homepage.html", name_string=session['user'])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)



def authenticate_func(staff, fname, password):
    """Setup the connection to Mongodb for this microservice"""
    cluster = MongoClient("mongodb+srv://admin:SOFT7011db@cluster0.0ojaw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = cluster["vaccinedb"]
    collection = db["users"]

    ans = False

    inputted_password = password.encode("utf-8")
    encoded_password = base64.b64encode(inputted_password)
    x = list(collection.find({"staff": str(staff)}))
    if x:
        x = x[0]
        db_fname = x["firstName"]
        db_password = x["password"]
        db_staff = x["staff"]
        x = encode(x)
        if str(staff) != str(db_staff) or str(fname) != str(db_fname) or str(encoded_password) != str(db_password):
            print("Error, credentials are incorrect")
            return ans, x
        elif str(staff) == str(db_staff) and str(fname) == str(db_fname) and str(encoded_password) == str(db_password):
            # if all 3 credentials match the DB, the user is authentified for access
            print("Password, Name and ID all match!")
            ans = True
            return ans, x

    else:
        print("Error, staff number not in database")
        return ans, x


def encode(o):
    if '_id' in o:
        o['_id'] = str(o['_id'])
    return o


def account_manager_updater(cp, list):
    size = len(list)
    attr_list = ["fname", "sname", "address", "email", "gender", "job", "staff", "telephone"]
    vc = vaccineAccountManager
    x = vc.return_cp_db(vc, cp)
    x = encode(x)
    crownID = x["crownpassID"]
    if str(crownID) == str(cp):
        for i in range(size):
            vc.manage_user_update_details(vc, cp, attr_list[i], list[i])
    else:
        print("Error: user doesn't match the user pulled from the database")




