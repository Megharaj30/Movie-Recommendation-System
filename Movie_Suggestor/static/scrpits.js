// scripts.js
document.addEventListener('DOMContentLoaded', function () {
    console.log("The page is fully loaded and scripts are ready to run!");
    
    // Example using jQuery for a hover effect on movie items
    $(document).ready(function() {
        $('.list-group-item').hover(function() {
            $(this).css('transform', 'scale(1.05)');
        }, function() {
            $(this).css('transform', 'scale(1)');
        });
    });
    
    // Add more interactive JavaScript here
});

