
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
#client = MongoClient("mongodb+srv://yuvadaranee:pakkiyou@cluster0.vbepewq.mongodb.net/test?retryWrites=true&w=majority", ssl=True)
client = MongoClient("mongodb://localhost:27017")
db = client['flight_booking']
users_collection = db['users']
flights_collection = db['flights']
bookings_collection =db['bookings']

# Routes for user functionalities

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #if 'user_id' in session:
    #   return redirect('/dashboard')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = users_collection.find_one({'user': username})

        if existing_user:
            return render_template('signup.html', error='Username already exists. Try to login!!')

        user_data = {'user': username, 'password': password, "role": "user"}
        user_id = users_collection.insert_one(user_data).inserted_id

        session['user_id'] = str(user_id)
       # return redirect('/dashboard')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['user']
        password = request.form['password']
        user_ = users_collection.find_one({'user': username, 'password': password})
           
        if user_ and user_['role'] == 'admin':
            session['user_id'] = str(user_['_id'])
            return redirect('/admin_dashboard')
        
        else:
            
            if user_:
                session['user_id'] = str(user_['_id'])
                return redirect('/dashboard')
            
            else :
            
                return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        return render_template('dashboard.html',user=user)
    else:
        return redirect('/login')

@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user=users_collection.find_one({'user':username,'password':password})
        
        if user and user['role'] == 'admin':
            session['user_id'] = str(user['_id'])
            return redirect('/admin_dashboard')
        else:
            return render_template('admin_login.html', admin_error='Invalid admin credentials')

    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html',msg='You have been logged out')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        return render_template('admin_dashboard.html', user=user, flights=flights_collection.find(), bookings=bookings_collection.find())
    else:
        return redirect('/login')

@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        start = request.form['start']
        end = request.form['end']
        time1 = request.form['time1']
        time2 = request.form['time2']
        
        existing_flight = flights_collection.find_one({'number':number})
        if existing_flight:
            if 'user_id' in session:
                user_id = session['user_id']
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            return render_template('admin_dashboard.html', user=user, flights=flights_collection.find(), bookings=bookings_collection.find(),msg='Added centre is already existed')
        else:    
            flight={'name': name,'number': number,'start': start,'end': end,'time1': time1,'time2':time2,'seats':60}
            flight_id=flights_collection.insert_one(flight).inserted_id
        return redirect('/admin_dashboard')

    return render_template('add_flight.html')


@app.route('/my_booking')
def my_booking():
    if 'user_id' in session:
        user_id=session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        bookings = bookings_collection.find({'user':user['user']})
        if bookings:
            return render_template('my_booking.html',bookings=bookings,value=True)
        else:
            return render_template('my_booking.html',value=False)
    return render_template('dashboard.html',user=user)

@app.route('/search_flight', methods=['POST','GET'])
def search_flight():
    if 'user_id' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            name = request.form['name']
            number = request.form['number']
            start = request.form['start']
            end = request.form['end']

        # Build the filter query based on the provided criteria
            filter_query = {}
            if name:
                filter_query['name'] = name
            if number:
                filter_query['number'] = number
            if start:
                filter_query['start'] = start
            if end:
                filter_query['end'] = end

        # Retrieve flights based on the filter criteria
        flights = flights_collection.find(filter_query)
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        return render_template('dashboard.html',flights=flights,user=user)  # Render the form initially
    
    else:
        return redirect('/dashboard')

@app.route('/book_flight',methods=['POST'])
def book_flight():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
    if request.method=='POST':
        book_user = request.form['book_user']
        book_number = request.form['book_number']
        book_name = request.form['book_name']
        book_start = request.form['book_start']
        book_end = request.form['book_end']
        book_time = request.form['book_time']
        book_date = request.form['book_date']
        book_seats = int(request.form['book_seats'])
    
        hash = '#'+book_user+'@'+ book_number + book_date + book_time
    
        existing_hash = bookings_collection.find_one({'hash': hash})

        if existing_hash:
            return render_template('dashboard.html', user=user, flights=flights_collection.find(), error='You have already Booked !!!')
        
        booking={'hash':hash,'user':book_user,'number':book_number, 'name':book_name, 'start':book_start, 'end':book_end, 'date':book_date,'booked_time':book_time,'booked_seats':book_seats}
    
        booking_id=bookings_collection.insert_one(booking).inserted_id
        flights_collection.update_one({'number':(book_number)}, {'$inc' : {'seats':-book_seats}})
        bookings = bookings_collection.find({'user':user['user']})
        if bookings:
            return render_template('my_booking.html',bookings=bookings,booking=booking,value=True)
        return render_template('my_booking.html',booking=booking)
        
    return render_template('dashboard.html', user=user, flights=flights_collection.find())
    
    

def validate_and_book_seats(booked_seats):
    for flight_id, seats in booked_seats.items():
        flight = db.flights_collections.find_one({'_id': flight_id})
        if not flight:
            return "Invalid flight selected."
        if seats > flight['available_seats']:
            return f"Error: Not enough seats available for {flight['name']} ({flight['number']})."
    return None


if __name__ == '__main__':
    app.run(debug=True)

