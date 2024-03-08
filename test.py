from unittest import TestCase

from app import app
from models import db, User
from flask_login import login_user

import requests_mock
import re  # Import the regex module
import os
from bs4 import BeautifulSoup


app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://superdb:superdbpassword@127.0.0.1/ingredish_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['LOGIN_DISABLED'] = True

db.drop_all()
db.create_all()

class RecipesTestCase(TestCase):

    @classmethod
    def setUpClass(self):

        # List of (pattern, response) tuples
        url_responses = [
            (r'https://api\.spoonacular\.com/recipes/random\?apiKey=[^&]+&number=20', 'GET', 'random_recipes.json'),
            (r'https://api\.spoonacular\.com/recipes/\d+/information\?apiKey=[^&]+', 'GET', 'recipe.json'),
            (r'https://api\.spoonacular\.com/recipes/complexSearch.*', 'GET', 'complex_search.json'),
            (r'https://api\.spoonacular\.com/recipes/findByIngredients\?apiKey=.+&ingredients=.+', 'GET', 'findByIngredients.json'),
            # Add more patterns and responses as needed
        ]

        self.mocker = requests_mock.Mocker()
        self.mocker.start()  # Start the mocker

        # Define the base path to your resources folder
        resources_path = os.path.join(os.path.dirname(__file__), 'resources')

        # Iterate over the patterns and file names, creating a mock for each
        for pattern, method, file_name in url_responses:
            file_path = os.path.join(resources_path, file_name)
            with open(file_path, 'r') as file:
                response_data = file.read()
            self.mocker.register_uri(method, re.compile(pattern), text=response_data, status_code=200)

        user = User(
            username="spinderman",
            password="blabla",
            first_name="Spider", 
            last_name="Man", 
            email="spiderman@gmail.com")
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.mock_user = user

    def setUp(self):
        super().setUp()  # Ensure proper setup if using a setup method from a superclass
        self.client = app.test_client(use_cookies=True)
        with self.client as c:
            with c.session_transaction() as sess:
                sess['userid'] = self.user_id 

    @classmethod
    def tearDownClass(self):
        db.session.rollback()
        self.mocker.stop()  # Ensure to stop the mocker

    def test_home(self):
        with self.client as client:
            response = client.get("/")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('https://spoonacular.com/recipeImages/638772-556x370.jpg', html)

    def test_recipe_detail(self):
        with self.client as client:
            response = client.get("/recipe/511728")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('https://spoonacular.com/recipeImages/511728-556x370.jpg', html)
            self.assertIn('511728', html)

    def test_search(self):
        with self.client as client:
            response = client.post("/search", data={'search-bar': 'pasta'})
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Pasta With Tuna', html)
            self.assertIn('Pasta Margherita', html)
            self.assertIn('https://spoonacular.com/recipeImages/654959-312x231.jpg', html)
            self.assertIn('https://spoonacular.com/recipeImages/511728-312x231.jpg', html)

    def test_favorites(self):
        with self.client as client:
            
            # add a recipe to DB by calling get recipe
            response = client.get("/recipe/511728")
            
            # Find the <span> element with the 'data-recipe-id' attribute and extract recipe.id
            soup = BeautifulSoup(response.data, 'html.parser')
            span = soup.find('span', attrs={'data-recipe-id': True})
            recipe_id = span['data-recipe-id'] if span else None

            # add the recipe.id as favorite
            response = client.post(f"/favorite/{recipe_id}")
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Ok', html)

            # check it is in favorites
            response = client.get(f"/favorites")
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(f"Pasta Margherita", html)

            # remove the recipe.id from favorites
            response = client.post(f"/unfavorite/{recipe_id}")
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Ok', html)

            # check it is not in favorites
            response = client.get(f"/favorites")
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(f"Pasta Margherita", html)
           
    def test_pantry(self):
        with self.client as client:
            ### add apple, milk and pepper to pantry
            response = client.post("/pantry", data={'item_name': 'apple'})
            response = client.post("/pantry", data={'item_name': 'milk'})
            response = client.post("/pantry", data={'item_name': 'pepper'})

            ### check apple, milk and pepper are in the pantry
            response = client.get("/pantry")
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('apple', html)
            self.assertIn('milk', html)
            self.assertIn('pepper', html)

            ### Extract pepper item_id
            soup = BeautifulSoup(html, 'html.parser')
            # Find the <span> with the pantry item text "pepper"
            pepper_span = soup.find('span', text='pepper')
            # Navigate up to the parent <form> and extract the action attribute
            pepper_form = pepper_span.find_parent('form')
            action_url = pepper_form['action']
            # Extract the pepper ID from the action URL
            pepper_id = action_url.split('/')[-1]  # Assuming the ID is the last part of the URL
            self.assertIsNotNone(pepper_id)

            # remove pepper from pantry
            response = client.post(f"/remove_pantry/{pepper_id}")

            # check apple and milk are in the pantry, but pepper is not
            response = client.get("/pantry")
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('apple', html)
            self.assertIn('milk', html)
            self.assertNotIn('pepper', html)

            #search with pantry
            response = client.post("/search_with_pantry")
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Swiss Bircher Muesli', html)
            self.assertIn('Grand Apple and Cinnamon Biscuits', html)