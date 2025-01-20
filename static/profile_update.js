// Function to open the form dynamically based on the form ID
function openForm(formId) {
    
    var profileUpdateForm = document.getElementById('profileUpdateForm');
    var PLZupdateForm = document.getElementById('PLZupdateForm');
    var openTimeUpdateForm = document.getElementById('openTimeUpdateForm')
    var Profile = document.getElementById('Profile');
    var showOpenTime = document.getElementById('showOpenTime')
    var showPLZ = document.getElementById('showPLZ')
    profileUpdateForm.style.display = 'none';
    PLZupdateForm.style.display = 'none';
    Profile.style.display = 'none'
    openTimeUpdateForm.style.display = 'none'
    showOpenTime.style.display = 'none'
    showPLZ.style.display = 'none'

    // Show the selected form
    var selectedForm = document.getElementById(formId);
    selectedForm.style.display = 'block';
}

// Function to close the form dynamically based on the form ID
function closeForm(formId) {
    var form = document.getElementById(formId);
    form.style.display = 'none';
    Profile.style.display = 'block'
}

function addInput(element) {
    if (element.nextElementSibling) return; // Prevent duplicate additions
    
    let newInput = document.createElement("input");
    newInput.type = "number";
    newInput.oninput = function() { addInput(this); };
    
    document.getElementById("input-container").appendChild(newInput);
}

function sendData() {
    let inputs = document.querySelectorAll("#input-container input");
    let values = [];

    inputs.forEach(input => {
        if (input.value.trim() !== "") {
            values.push(input.value.trim());
        }
    });

    fetch("/update_PLZ", {
        method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
        body: JSON.stringify({ inputs: values })
        
    })
    alert("Updated")
    window.location.reload();
}
