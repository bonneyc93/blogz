from flask import Flask,render_template,request,flash,session,redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogger@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "hello"

class Blog(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))

    def __init__(self,title,body):
        self.title = title
        self.body = body

@app.route('/blog')
def blog_post():
    id = request.args.get("id")
    
    if id is not None:
        id = int(id)
        blog = Blog.query.filter_by(id=id).first()
        return render_template('blogentry.html',blog=blog)

    if id == None:
        blog_posts = Blog.query.all()
        return render_template('blog.html',blog_posts=blog_posts)

@app.route('/newpost', methods=['POST','GET'])
def new_post():
        
    if request.method == 'POST':
        title= request.form['blogtitle']
        body= request.form['blogbody']

        if title == "":
            flash("Please fill out all fields.")
            return render_template('newpost.html',blogbody=body)
        
        if body == "":
            flash("Please fill out all fields.")
            return render_template('newpost.html',blogtitle= title)
           
        blogbody = Blog(title,body)
        db.session.add(blogbody)
        db.session.commit()
        id = blogbody.id
        id = str(id)
        blog = Blog.query.filter_by(id=id).first()
        return redirect('/blog?id=' + id)
    
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()