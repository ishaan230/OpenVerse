from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import config
import certifi
import requests
from requests import get
from datetime import datetime
import os



app = Flask(__name__)
app.config.from_object(config)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#set up MongoDB
client = MongoClient(config.MONGO_URI)
db = client.gettingStarted
col = db.usrpass
perdet = db.people
blogg = db.blogDetails
current_date = datetime.now().date()
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = col.find_one({'username': username})
        if user and password==user['password']:
            session['username'] = username
            return redirect(url_for('welcome'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            if col.find_one({'username': username}):
                return render_template('register.html', error='UserName Already Exists!')

            col.insert_one({'username': username, 'password': password})
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Passwords do not match')
    return render_template('register.html')



@app.route('/welcome')
def welcome():
    print(session)
    print(type(session))
    if 'username' in session:
        return render_template('welcome.html', username=session['username'],current_date=current_date)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    print('logges out....')
    return redirect(url_for('login'))

@app.route('/blogDetails')
def blogDet():
    return render_template('blogDetailed.html')
@app.route('/blog')
def sub_team():
    if 'username' in session:
        return render_template('blog.html')

# @app.route('/form_submit', methods=['GET','POST'])
# def form_submission():
#     if 'username' in session:
#         username = session['username']
#         if request.method == 'POST':
#             blogTitle = request.form['title']
#             blogContent = request.form['blogCont']
#             blogg.insert_one({'userid': username,'blogContent': blogContent,'title':f'{blogTitle}'})
#             return render_template('welcome.html')
#     else:
#         print("Not in if")
#     return render_template('blog.html')

@app.route('/form_submit', methods=['GET', 'POST'])
def form_submission():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            blogTitle = request.form['title']
            blogContent = request.form['blogCont']
            
            # Check if the post request has the file part
            if 'blogPic' in request.files:
                file = request.files['blogPic']
                # If the user does not select a file, the browser submits an empty file without a filename
                if file.filename == '':
                    return 'No selected file'
                if file:
                    # Save the file to the uploads folder
                    filename = file.filename
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    print("File path: ",file_path)
                    # # Save the file path to MongoDB along with other form data
                    # client = MongoClient('mongodb://localhost:27017/')
                    # db = client['your_database_name']
                    # collection = db['your_collection_name']

                    file_doc = {
                        'userid': username,
                        'title': blogTitle,
                        'blogContent': blogContent,
                        'file_path': file_path
                    }
                    blogg.insert_one(file_doc)
                    return render_template('welcome.html')
        else:
            print("Not in if")
    return render_template('blog.html')


@app.route('/home')
def home():
    login = 0
    homeBlog = []
    blogs = blogg.find({})
    for document in blogs:
        blog_content = document['blogContent']
        title = document['title']
        username = document['userid']
        pic = document['file_path']
        homeBlog += [[username,title,blog_content,pic]]
    # print(homeBlog)
    if 'username' in session:
        login = 1
    
    return render_template('home.html',data = homeBlog,login=login)

@app.route('/view')
def view():
    if 'username' in session:
        username = session['username']
        cursor = blogg.find({'userid': f'{username}'})
        viewBlog = []
        for document in cursor:
            blog_content = document['blogContent']
            title = document['title']
            pic = document['file_path']
            viewBlog += [[username,title,blog_content,pic]]
        return render_template('views.html',data = viewBlog)

@app.route('/delete_all')
def deleteall():
    username = session['username']
    blogg.delete_many({'userid':f'{username}'})
    return render_template('welcome.html')

@app.route('/delete_one')
def deleteone():
    username = session['username']
    
    blogg.delete_one({'userid':f'{username}'})

    return render_template('welcome.html')

@app.route('/update_post/<string:titlle>', methods=['POST'])
def update_post(titlle):
    # Get the updated content from the request
    updated_content = request.form['content']

    blogs = blogg.find({"title": titlle})
    result = blogg.update_many({"title": titlle}, {"$set": {"blogContent": updated_content}})
    print(blogs)
    print('Testing!!!!!!!#######################################################')
    return redirect('/view')


if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)