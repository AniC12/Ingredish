import requests
from models import Recipe, Product, Ingredient

MY_KEY = "ebd16308c21c4f8da26e8f0874aecafb"

def get_random_recipes():

    response = requests.get(f'https://api.spoonacular.com/recipes/random?apiKey={MY_KEY}&number=10')
    if response.status_code == 200:
        recipes_data = response.json()
        random_recipes = recipes_data['recipes']
    else:
        random_recipes = []

    return random_recipes

def get_recipe_details(api_id):

    response = requests.get(f'https://api.spoonacular.com/recipes/{api_id}/information?apiKey={MY_KEY}')
    if response.status_code == 200:
        data = response.json()

        recipe = Recipe()
        recipe.api_id = api_id
        recipe.image = data.get('image')
        recipe.title = data.get('title')
        recipe.description = data.get('instructions')
        recipe.servings = data.get('servings')
        for json_ingredient in data.get('extendedIngredients'):

            product = Product.query.filter_by(name=json_ingredient.get('name')).first()

            if product is None:            
                product = Product()
                product.name = json_ingredient.get('name')
            
            ingredient = Ingredient()
            ingredient.amount = json_ingredient.get('amount')
            ingredient.unit = json_ingredient.get('unit')
            ingredient.product = product

            recipe.ingredients.append(ingredient)
        return recipe 
    

def get_recipes(query):

    response = requests.get(
            'https://api.spoonacular.com/recipes/complexSearch', 
            params={"query": query, "apiKey": MY_KEY, "number": 10}
        )
    if response.status_code == 200:
        recipes_data = response.json()
        list_of_recipes = recipes_data.get('results')
    else:
        list_of_recipes = []

    return list_of_recipes

def get_recipes_pantry(pantry_items):

    response = requests.get(
            f'https://api.spoonacular.com/recipes/findByIngredients?apiKey={MY_KEY}&ingredients={",".join(pantry_items)}'
        )
    
    if response.status_code == 200:
        return response.json()
    return []