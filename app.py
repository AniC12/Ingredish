from flask import Flask, request, redirect, render_template, session, flash
from models import db, connect_db, User, Recipe, Product, Ingredient, Favorite, Pantry
from forms import UserSignUpForm, UserLoginForm, SearchForm
from api import get_random_recipes, get_recipe_details, get_recipes, get_recipes_pantry
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import login_required, login_user, logout_user, LoginManager
from sqlalchemy.exc import IntegrityError
from werkzeug.urls import url_encode
import os


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bloglyuser:bloglypassword@localhost/ingredish'
app.config['SQLALCHEMY_DATABASE_URI'] = os.gentenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

app.config['SECRET_KEY'] = os.gentenv("SECRET_KEY")
debug = DebugToolbarExtension(app)

login_manager = LoginManager(app)
login_manager.login_view = 'show_login_form'


@login_manager.user_loader
def get_user(id):
    return User.query.get(int(id))


def get_current_user():
    cur_user = User.query.get(session.get('userid'))

    return cur_user


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
    session['userid'] = new_user.id
    login_user(new_user)
    flash('Welcome! Successfully Created Your Account!', "success")

    return redirect('/')


@app.route('/login')
def show_login_form():
    form = UserLoginForm()

    return render_template('login.html', form=form)


@app.route('/login', methods=['POST'])
def login():
    form = UserLoginForm()

    username = form.username.data
    password = form.password.data
    user = User.authenticate(username, password)
    if user:
        flash(f"Welcome Back, {user.username}!", "primary")
        login_user(user)
        session['userid'] = user.id
        return redirect('/')
    else:
        form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('userid')
    logout_user()
    flash("Goodbye!", "info")
    return redirect('/')


@app.route('/recipe/<string:api_id>')
def show_recipe(api_id):
    recipe = Recipe.query.filter_by(api_id=api_id).first()
    if recipe:
        return render_template('recipe_detail.html', recipe=recipe, fav=Favorite.check_favorite(recipe.id))

    recipe = get_recipe_details(api_id)

    if recipe is None:
        return render_template('error.html')

    db.session.add(recipe)
    db.session.commit()

    return render_template('recipe_detail.html', recipe=recipe, fav=Favorite.check_favorite(recipe.id))


@app.route('/search', methods=['POST'])
def search_recipe():
    query = request.form.get('search-bar', '')
    list_of_recipes = get_recipes(query)

    session['query'] = query
    session['recipes'] = list_of_recipes

    return render_template('search_page.html', recipes=list_of_recipes, search_text=query)


@app.route('/search', methods=['GET'])
def show_search_page():

    query = session.get('query')
    list_of_recipes = session.get('recipes')

    return render_template('search_page.html', recipes=list_of_recipes, search_text=query)


@app.route('/favorite/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_favorite(recipe_id):
    user = get_current_user()

    favorite_recipe = Favorite.query.filter_by(
        user_id=user.id, recipe_id=recipe_id).first()
    if favorite_recipe is None:
        new_favorite = Favorite(user_id=user.id, recipe_id=recipe_id)
        db.session.add(new_favorite)
        db.session.commit()

    return "Ok"


@app.route('/unfavorite/<int:recipe_id>', methods=['POST'])
@login_required
def untoggle_favorite(recipe_id):
    user = get_current_user()

    favorite_recipe = Favorite.query.filter_by(
        user_id=user.id, recipe_id=recipe_id).first()
    if favorite_recipe:
        db.session.delete(favorite_recipe)
        db.session.commit()

    return "Ok"


@app.route('/favorites')
@login_required
def show_favorites():
    user = get_current_user()

    user_favorite_recipe_ids = [
        favorite.recipe_id for favorite in user.favorite_recipes]
    favorite_recipes = Recipe.query.filter(
        Recipe.id.in_(user_favorite_recipe_ids)).all()

    return render_template('favorites.html', recipes=favorite_recipes)


@app.route('/pantry')
@login_required
def show_pantry():
    user = get_current_user()

    pantry_items = user.pantry_items

    return render_template('pantry.html', pantry_items=pantry_items)


@app.route('/pantry', methods=['POST'])
@login_required
def add_to_pantry():
    user = get_current_user()
    item_name = request.form.get('item_name')

    product = Product.query.filter_by(name=item_name).first()

    if product is None:
        product = Product()
        product.name = item_name
        db.session.add(product)

    new_item = Pantry(user_id=user.id, product_id=product.id)
    item = Pantry.query.filter_by(product_id=product.id).first()

    if item is None:
        new_item = Pantry(user_id=user.id, product_id=product.id)
        db.session.add(new_item)

    db.session.commit()

    pantry_items = user.pantry_items
    return render_template('pantry.html', pantry_items=pantry_items)


@app.route('/remove_pantry/<int:item_id>', methods=['POST'])
@login_required
def remove_pantry(item_id):
    user = get_current_user()
    item_to_remove = Pantry.query.get(item_id)

    if item_to_remove and item_to_remove.user_id == user.id:
        db.session.delete(item_to_remove)
        db.session.commit()

    return redirect('/pantry')


@app.route('/search_with_pantry', methods=['POST'])
@login_required
def search_with_pantry():
    user = get_current_user()
    pantry_items = [item.product.name for item in user.pantry_items]

    list_of_recipes = get_recipes_pantry(pantry_items)

    return render_template('pantry_results.html', recipes=list_of_recipes)
