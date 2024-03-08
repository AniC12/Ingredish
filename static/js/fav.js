function makeFavorite() {
    const recipeId = this.getAttribute('data-recipe-id');

    axios.post('/favorite/' + recipeId)
        .then(response => {
            if (response.data === "Ok") {
                this.classList.add('checked');
                this.removeEventListener('click', makeFavorite);
                this.addEventListener('click', unmakeFavorite);
            }
            // Update the UI if needed based on the response from the server
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function unmakeFavorite() {
    const recipeId = this.getAttribute('data-recipe-id');

    axios.post('/unfavorite/' + recipeId)
        .then(response => {
            if (response.data === "Ok") {
                this.classList.remove('checked');
                this.removeEventListener('click', unmakeFavorite);
                this.addEventListener('click', makeFavorite);
            }
            // Update the UI if needed based on the response from the server
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

document.addEventListener('DOMContentLoaded', function () {
    let elements = document.getElementsByClassName('fa fa-star');

    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener('click', makeFavorite);
    }

    elements = document.getElementsByClassName('fa fa-star checked');

    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener('click', unmakeFavorite);
    }
});
