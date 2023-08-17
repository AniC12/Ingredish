from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
DEFAULT_RECIPE_IMAGE_URL = "https://www.freeiconspng.com/uploads/food-utensils-png-icon-11.png"
DEFAULT_PRODUCT_IMAGE_URL = "https://www.freeiconspng.com/uploads/agriculture-food-17.png"

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False,  unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False,  unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)


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
    image = db.Column(db.Text, nullable=False, default=DEFAULT_RECIPE_IMAGE_URL)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    servings = db.Column(db.Integer)
    api_id = db.Column(db.Integer)
    ingredients = db.relationship("Ingredient")

class Product(db.Model):

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.Text, nullable=False, default=DEFAULT_PRODUCT_IMAGE_URL)
    name = db.Column(db.Text, nullable=False)
    api_id = db.Column(db.Integer)

class Ingredient(db.Model):

    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    amount = db.Column(db.Integer)
    unit = db.Column(db.String)
    product = db.relationship("Product")

class Favorite(db.Model):

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Pantry(db.Model):

    __tablename__ = 'pantry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
