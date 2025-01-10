// Function to open the form dynamically based on the form ID
function openForm(formId) {
    // Hide both forms initially
    var userForm = document.getElementById('userForm');
    var restaurantForm = document.getElementById('restaurantForm');
    userForm.style.display = 'none';
    restaurantForm.style.display = 'none';

    // Show the selected form
    var selectedForm = document.getElementById(formId);
    selectedForm.style.display = 'block';
}

// Function to close the form dynamically based on the form ID
function closeForm(formId) {
    var form = document.getElementById(formId);
    form.style.display = 'none';
}
