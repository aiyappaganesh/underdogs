$(document).ready(function(){
    $(window).scroll(function(){
        var top_of_window = $(window).scrollTop();
        var section2 = $('#section-2').offset().top;
        if(top_of_window >= section2-50) {
            $('header').removeClass('no-navbar');
            $('#nav-section-2').addClass('blue-background');
            $('#nav-section-2 a').addClass('white-font');
        } else {
            $('header').addClass('no-navbar');
        }
    });
});