from flask import Flask, request, redirect, render_template, session, flash
from models import db, connect_db, User, Recipe, Product, Ingredient, Favorite, Pantry
from forms import UserSignUpForm, UserLoginForm, SearchForm
from api import get_random_recipes, get_recipe_details, get_recipes
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bloglyuser:bloglypassword@localhost/ingredish'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)


@app.route("/")
def show_home_page():
    """Show home page with random recipes"""
    
    random_recipes = get_random_recipes()

    return render_template('index.html', recipes=random_recipes)


@app.route('/signup', methods=['GET'])
def show_signup_form():
    form = UserSignUpForm()

    return render_template('signup.html', form=form)

@app.route('/signup', methods=['POST'])
def signup_user():
    form = UserSignUpForm()

    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    new_user = User.signup(username, password, email, first_name, last_name)

    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        form.username.errors.append('Username taken.  Please pick another')
        return render_template('register.html', form=form)
    session['username'] = new_user.username
    flash('Welcome! Successfully Created Your Account!', "success")
    
    return redirect('/')

@app.route('/login')
def show_login_form():
    form = UserLoginForm()

    return render_template('login.html', form=form)
    
@app.route('/login', methods=['POST'])
def login_user():
    form = UserLoginForm()

    username = form.username.data
    password = form.password.data
    user = User.authenticate(username, password)
    if user:
        flash(f"Welcome Back, {user.username}!", "primary")
        session['username'] = user.username
        return redirect('/')
    else:
        form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')

@app.route('/recipe/<string:api_id>')
def show_recipe(api_id):
    recipe = Recipe.query.filter_by(api_id=api_id).first()

    if recipe:
        return render_template('recipe_detail.html', recipe=recipe)
    
    recipe = get_recipe_details(api_id)

    if recipe is None:
        return render_template('error.html')

    db.session.add(recipe)
    db.session.commit()

    return render_template('recipe_detail.html', recipe=recipe)


@app.route('/search', methods=['POST'])
def search_recipe():
    query = request.form.get('search-bar','')
    list_of_recipes = get_recipes(query)

    session['query'] = query
    session['recipes'] = list_of_recipes

    return render_template('search_page.html', recipes=list_of_recipes, search_text=query)


@app.route('/search', methods=['GET'])
def show_search_page():

    query = session.get('query')
    list_of_recipes = session.get('recipes')

    return render_template('search_page.html', recipes=list_of_recipes, search_text=query)