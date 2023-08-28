
# Ingredish - Recipe Search and Pantry Management Web Application


## Project Overview ##


- **URL: My Deployed URL**


- **GitHub Repository: [https://github.com/AniC12/ingredish](https://github.com/AniC12/ingredish)**

## Description ##
Ingredish is a web application that allows users to search for recipes, manage their pantry items, and find recipes based on the ingredients available in their pantry. Users can create an account, log in, and access a variety of features to make their cooking experience more convenient and enjoyable.

## Features Implemented ##




- **User Authentication (Login/Signup/Logout):**
Implemented user authentication to ensure secure access to the application. This feature allows users to create an account, log in, and log out.

- **Random Recipes Display:**
Users can view a list of randomly selected recipes on the homepage. This provides inspiration and variety for meal planning.



- **Recipe Detail View:**
Clicking on a recipe title leads to a detailed recipe page. Users can access recipe instructions and additional information.



- **Mark Recipes as Favorites:**
Users can mark recipes as their favorites, which are saved for easy access in their profile.



- **Pantry Management:**
Users can add and remove pantry items. Pantry items are then used to search for recipes based on available ingredients.



- **Search Recipes with Pantry Ingredients:**
Users can perform recipe searches based on the ingredients they have in their pantry.
## User Flow ##

1. User arrives at the homepage.
2. User can either log in or sign up to access their account.
3. After logging in, the user can view randomly selected recipes on the homepage.
4. The user can navigate to a recipe detail page to learn more about a specific recipe.
5. The user can mark recipes as favorites and access them later in their profile.
6. The user can manage their pantry by adding, viewing, and removing items.
7. The user can initiate a recipe search using their pantry ingredients.
8. The search results are displayed, allowing the user to explore recipes.

## Spoonacular API ##
The application uses the [Spoonacular API](https://api.spoonacular.com "Spoonacular API") to retrieve recipe data and perform ingredient-based searches.

## Technology Stack ##


- Frontend: HTML, CSS, Jinja


- Backend: Python, Flask


- Database: SQLAlchemy


- Authentication: Flask-Login