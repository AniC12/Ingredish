from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from app import session


db = SQLAlchemy()
bcrypt = Bcrypt()
DEFAULT_RECIPE_IMAGE_URL = "https://www.freeiconspng.com/uploads/food-utensils-png-icon-11.png"


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False,  unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False,  unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    favorite_recipes = db.relationship(
        'Favorite', backref='users', lazy='dynamic')
    pantry_items = db.relationship('Pantry', backref='users', lazy='dynamic')

    @classmethod
    def signup(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username,
                   password=hashed_utf8,
                   email=email,
                   first_name=first_name,
                   last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class Recipe(db.Model):

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.Text, nullable=False,
                      default=DEFAULT_RECIPE_IMAGE_URL)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    servings = db.Column(db.Integer)
    api_id = db.Column(db.Integer)
    ingredients = db.relationship(
        "Ingredient", backref='recipes', lazy='dynamic')


class Product(db.Model):

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    api_id = db.Column(db.Integer)


class Ingredient(db.Model):

    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey(
        'recipes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), nullable=False)
    amount = db.Column(db.Integer)
    unit = db.Column(db.String)
    product = db.relationship("Product")


class Favorite(db.Model):

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey(
        'recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @classmethod
    def check_favorite(cls, recipe_id):
        user = User.query.get(session.get('userid'))
        if user:
            favorite_recipe = Favorite.query.filter_by(
                user_id=user.id, recipe_id=recipe_id).first()
            if favorite_recipe:
                return "2"
            return "1"
        return "0"


class Pantry(db.Model):

    __tablename__ = 'pantry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), nullable=False)
    product = db.relationship("Product")
