document.getElementById('uploadForm').addEventListener('submit', function(event){
    const fileInput = document.getElementById('formFileLg');
    const errorMessage = document.getElementById('errorMessage');
    const file = fileInput.files[0];

    if (file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
            errorMessage.innerHTML = `<div class="alert alert-danger" role="alert">Image File Invalid</div>`;
            event.preventDefault(); 
        } else {
            errorMessage.innerHTML = '';
        }
    } else {
        errorMessage.innerHTML = `<div class="alert alert-danger" role="alert">Please select a file</div>`;
        event.preventDefault(); 
    }
});
function setTwoNumberDecimal() {
    const priceInput = document.querySelector('input[name="price"]');
    const value = parseFloat(priceInput.value);
    if (!isNaN(value)) {
        priceInput.value = value.toFixed(2);
    }
}

function changeLike(){
    likes = localStorage.getItem("likes") || 0
    console.log(likes)
    // get the innerHTML for like and dislike
    let likeElement = document.getElementById("js-like-button")
    // change the Inner HTML for like and dislike
    if (likeElement.innerHTML == '<button type="button" class="btn btn-outline-primary">Like</button>'){
        likeElement.innerHTML = '<button type="button" class="btn btn-primary">Like</button>'
        likes++
        localStorage.setItem("likes",`${likes}`)
    }
    else{
        likeElement.innerHTML = '<button type="button" class="btn btn-outline-primary">Like</button>'
        likes--
        localStorage.setItem("likes",`${likes}`)

    }
    // add the like or dislike to the like or dislike count
    // store the count
}
function changeDislike(){
    // get the innerHTML for like and dislike
    let dislikeElement = document.getElementById("js-dislike-button")
    // change the Inner HTML for like and dislike

    // add the like or dislike to the like or dislike count
    // store the count
}

