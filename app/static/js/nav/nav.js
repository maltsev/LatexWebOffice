//setze den tab auf active, welcher gerade angezeigt wird
$(document).ready(function() {
    $('.nav li a').on('click', function() {
        $(this).parent().parent().find('.active').removeClass('active');
    });
    $('.nav').find('a[href="' + location.pathname + '"]').parents('li').addClass('active');
    
});
