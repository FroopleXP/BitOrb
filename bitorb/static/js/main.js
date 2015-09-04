$(document).ready(function(){
    // Drop down login 
    $('.dropdown-menu').find('form').click(function (e) {
        e.stopPropagation();
    });
});