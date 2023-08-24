function makeFavorite() {
    // Perform an AJAX POST request to the server
    var recipeId = this.getAttribute('data-recipe-id');

    fetch('/favorite/' + recipeId, {
        method: 'POST'
    })
    .then(response => response.text())
    .then(data => {
        if (data === "Ok") {
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
    // Perform an AJAX POST request to the server
    var recipeId = this.getAttribute('data-recipe-id');

    fetch('/unfavorite/' + recipeId, {
        method: 'POST'
    })
    .then(response => response.text())
    .then(data => {
        if (data === "Ok") {
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


document.addEventListener('DOMContentLoaded', function() {
    var elements = document.getElementsByClassName('fa fa-star');
    
    for (var i = 0; i < elements.length; i++) {
        elements[i].addEventListener('click', makeFavorite);
    }

    elements = document.getElementsByClassName('fa fa-star checked');
    
    for (var i = 0; i < elements.length; i++) {
        elements[i].addEventListener('click', unmakeFavorite);
    }

});



