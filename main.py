from flask import Flask,render_template,request,flash,session,redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "hello"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
   
@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        username_error = ''
        password_error = ''
        verify_error = ''
        
        if username == '':
            username_error = 'That is not a valid username'
        elif username.find(' ') >= 1:
            username_error = 'That is not a valid username' 
        elif len(username) < 3 or len(username) >20:
            username_error = 'That is not a valid username'
        elif username == existing_user:
            username_error = 'That name has already been taken'

        if password == '':
            password_error = 'That is not a valid password'
        elif password.find(' ') >= 1:
            password_error = 'Not a valid password.'
        elif len(password) < 3 or len(password) > 20:
            password_error = 'That is not a valid password'
        elif password != verify:
            password_error = 'Passwords do not match'
            verify_error = 'Passwords do not match'
        
        if username_error or password_error or verify_error:
            return render_template('signup.html', username=username, username_error=username_error, password='', password_error=password_error, verify='', verify_error=verify_error)    
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        username_error = ''
        password_error = ''

        if user and user.password == password:
            session['username'] = username          
            return redirect('/newpost')
        elif user and user.password != password:
            password_error = 'Invalid password'
        elif user and user.username != username:
            username_error = 'Invalid username'
        return render_template('login.html', username=username, username_error=username_error, password="", password_error=password_error)

    return render_template('login.html') 

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    if request.args.get('id'):     
        blog = Blog.query.filter_by(id=request.args.get('id')).first()
        user = User.query.filter_by(id=blog.owner_id).first()
        title = blog.title
        body = blog.body
        return render_template('blogentry.html',blog_title=title,blog_body=body, user=user)
    
    elif request.args.get('user'):      
        user = User.query.filter_by(id=request.args.get('user')).first()
        blogs = Blog.query.filter_by(owner_id=request.args.get('user'))
        return render_template('user.html', blogs=blogs, user=user)
          
    blogposts = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', blogposts=blogposts, users=users)
    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body'] 
        
        title_error = ''
        body_error = '' 
        
        if title == '':
            title_error = 'We need both a title and a body!'
        if body == '':
            body_error = 'We need both a title and a body!'

        if title_error != '' or body_error != '':
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, body=body)
        else:   
            new_blog = Blog(title,body,owner)
            db.session.add(new_blog)
            db.session.commit()  
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()