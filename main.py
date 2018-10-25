from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Twilight84*@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'BZv3qjEH&ZW5QyCR'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        flash("You must be logged in to use the blog.", 'error')
        return redirect('/login')


@app.route('/index', methods=['POST', 'GET'])
def index():
    
    users = User.query.all()

    return render_template('index.html',title="Blog Users",users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    blogs = Blog.query.all()

    return render_template('blog.html', title="Blog Posts", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        owner_id = User.query.filter_by(email=session['email']).first()
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ' '
        body_error = ' '
        if len(blog_title) == 0:
            title_error = 'Please fill out the title'
            body_error = 'Please fill out the body'
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
        if len(blog_body) == 0:
            body_error = 'Please fill out the body'
            title_error = 'Please fill out the title'
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
        else:
            new_blog = Blog(blog_title, blog_body, owner_id)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = str(new_blog.id)
      
            return redirect('/post?id={0}'.format(blog_id))
    
    return render_template('newpost.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']        

        if len(name) == 0:
            flash('Username field is empty', 'error')
        if len(email) == 0:
            flash('Email field is empty', 'error')
        if len(password) == 0:
            flash('Password field is empty', 'error')
        if len(verify) == 0:
            flash('Confirmation field is empty', 'error')
        if len(name) < 3:
            flash('Username must exceed 3 characters in length', 'error')
        if len(password) < 3:
            flash('Password must exceed 3 characters in length', 'error')
        if not password == verify:
            flash('Password and Confirmation do not match', 'error')

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user:
            new_user = User(name, email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
                   
            return redirect('/newpost')
        
        if existing_user:
            flash('Username already exists. Please try another name', 'error')

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Username does not exist', 'error')

        if user and user.password == password:
            session['email'] = email
            
            return redirect('/newpost')
        
        if user and user.password != password:
            flash('User password incorrect', 'error')


    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['email']
    flash('You have been successfully logged out', 'error')
    return redirect('/index')

@app.route('/post')
def single():

    blog_id = int(request.args.get('id', 'default id'))
    blog = Blog.query.get(blog_id)
    blog_owner = blog.owner
    blog_title = blog.title
    blog_body = blog.body
    username = blog.owner.name
    userid = blog.owner.id

    return render_template('post.html', blog_owner=blog_owner, blog_title=blog_title,
     blog_body=blog_body, username=username, userid=userid)

@app.route('/user')
def singleUser():

    owner_id = request.args.get('id', 'default id')
    blogs = Blog.query.filter_by(owner_id=owner_id).all()

    return render_template('singleUser.html', title="Blog Posts", blogs=blogs)




    

if __name__ == '__main__':
    app.run()