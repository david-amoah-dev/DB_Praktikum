//This is going to be the main JavaScript files

/* ________________________________________________________profile update.js Copy_______________________________________________________________*/
    const profileUpdateForm = document.getElementById('profileUpdateForm');

function openprofileForm() {
    // Show the selected form
    profileUpdateForm.showModal();
}
// Function to close the form dynamically based on the form ID
function closeprofileForm() {
    selectedForm.close();

/* _______________________________________________________login-popup.js Copy________________________________________________________________*/
    // Hide both forms initially
    const userForm = document.getElementById('userForm');
    const restaurantForm = document.getElementById('restaurantForm');

function openuserForm() {
    // Show the selected form
    userForm.showModal();
}
// Function to close the form dynamically based on the form ID
function closeuserForm() {
    userForm.close();
}

/* JavaScript Objects

    Customer
    function cstmobj(first, last, plz, adress, wallet) {
    this.firstName = first;
    this.lastName = last;
    this.plz = plz;
    this.adress = adress;
    this.wallet = wallet;
    update-function =
    }

    Restaurant
    function rstrobj(restname, plz, adress, wallet) {
    this.restname = restname;
    this.plz = plz;
    this.adress = adress;
    this.wallet = wallet;
    update-function =
    }

    Item
    function itmobj(name, price, img, desc) {
    this.name = name;
    this.price = price;
    this.img = img;
    this.desc = desc;
    update-function =
    }

    Order
    function ordrobj(orderid, total, itemdet) {
    this.orderid = orderid;
    this.total = total;
    this.itemid = img;
    }

*/

/* JavaScript Classes

    addToCart

    purchase

    confirmPurchase

    setState

    createNewItem

    createNewOrder

    editProfile -customer & restaurant #update



*/
