from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# ------------------ Models ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    whatsapp = db.Column(db.String(100))
    insta = db.Column(db.String(100))
    telegram = db.Column(db.String(100))
    facebook = db.Column(db.String(100))


class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(100))
    insta = db.Column(db.String(100))
    telegram = db.Column(db.String(100))
    facebook = db.Column(db.String(100))


# ------------------ Routes ------------------

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return redirect('/dashboard')
    else:
        return "Invalid Credentials"


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    whatsapp = request.form.get('whatsapp')
    insta = request.form.get('insta')
    telegram = request.form.get('telegram')
    facebook = request.form.get('facebook')

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        password=hashed_password,
        whatsapp=whatsapp,
        insta=insta,
        telegram=telegram,
        facebook=facebook
    )
    db.session.add(new_user)
    db.session.commit()

    return redirect('/')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard.html')


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']

    if request.method == 'POST':
        name = request.form['name']
        whatsapp = request.form.get('whatsapp')
        insta = request.form.get('insta')
        telegram = request.form.get('telegram')
        facebook = request.form.get('facebook')

        new_friend = Friend(
            user_id=user_id,
            name=name,
            whatsapp=whatsapp,
            insta=insta,
            telegram=telegram,
            facebook=facebook
        )
        db.session.add(new_friend)
        db.session.commit()

        return redirect('/friends')

    friends_list = Friend.query.filter_by(user_id=user_id).all()
    return render_template('friends.html', friends=friends_list)


@app.route('/edit_friend/<int:friend_id>', methods=['GET', 'POST'])
def edit_friend(friend_id):
    if 'user_id' not in session:
        return redirect('/')

    friend = Friend.query.get(friend_id)

    # Security check: friend belongs to the logged-in user
    if not friend or friend.user_id != session['user_id']:
        return "Unauthorized Access"

    if request.method == 'POST':
        friend.name = request.form['name']
        friend.whatsapp = request.form.get('whatsapp')
        friend.insta = request.form.get('insta')
        friend.telegram = request.form.get('telegram')
        friend.facebook = request.form.get('facebook')

        db.session.commit()
        return redirect('/friends')

    return render_template('edit_friend.html', friend=friend)


@app.route('/delete_friend/<int:friend_id>')
def delete_friend(friend_id):
    if 'user_id' not in session:
        return redirect('/')

    friend = Friend.query.get(friend_id)

    if not friend or friend.user_id != session['user_id']:
        return "Unauthorized Access"

    db.session.delete(friend)
    db.session.commit()

    return redirect('/friends')


@app.route('/chat/<int:friend_id>')
def chat(friend_id):
    if 'user_id' not in session:
        return redirect('/')

    friend = Friend.query.get(friend_id)

    if not friend or friend.user_id != session['user_id']:
        return "Unauthorized Access"

    links = {
        'whatsapp': f"https://wa.me/{friend.whatsapp}" if friend.whatsapp else None,
        'instagram': f"https://instagram.com/{friend.insta}" if friend.insta else None,
        'telegram': f"https://t.me/{friend.telegram}" if friend.telegram else None,
        'facebook': f"https://facebook.com/{friend.facebook}" if friend.facebook else None
    }

    return render_template('chat.html', friend=friend, links=links)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


# ------------------ Run App ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, host='0.0.0.0', port=5000)
