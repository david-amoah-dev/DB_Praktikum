let lastAlertedOrderId = null;  // Store the last alerted order ID
let initialCheck = true;  // Flag for the first run

// Function to check for new orders
async function checkForNewOrders() {
    try {
        console.log("Checking for new orders...");
        const response = await fetch('/check_new_orders');
        const data = await response.json();
        
        // Skip alert on the first run only if there are no orders
        if (initialCheck) {
            if (data.latest_order_id) {
                lastAlertedOrderId = data.latest_order_id;
            }
            initialCheck = false;
            return;
        }

        // Alert if a new order is detected and it's different from the last one alerted
        if (data.new_order && data.latest_order_id !== lastAlertedOrderId) {
            alert('A new order has been placed!');
            window.location.reload();

            lastAlertedOrderId = data.latest_order_id;  // Update the last alerted order ID
        }
    } catch (error) {
        console.error('Error fetching new orders:', error);
    }
}

// Check for new orders every 5 seconds
setInterval(checkForNewOrders, 5000);
