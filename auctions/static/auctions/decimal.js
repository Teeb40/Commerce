let items = 0;
document.getElementById('uploadForm').addEventListener('submit', function(event) {
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
