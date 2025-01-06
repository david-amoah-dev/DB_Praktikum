// Function to open the form dynamically based on the form ID
function openForm(formId) {
    
    var profileUpdateForm = document.getElementById('profileUpdateForm');
    profileUpdateForm.style.display = 'none';

    // Show the selected form
    var selectedForm = document.getElementById(formId);
    selectedForm.style.display = 'block';
}

// Function to close the form dynamically based on the form ID
function closeForm(formId) {
    var form = document.getElementById(formId);
    form.style.display = 'none';
}
