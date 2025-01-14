setInterval(function() {
    console.log("refresh");
    setTimeout(() => window.location.reload(), 100); // Small delay to allow message to print
}, 5000);
