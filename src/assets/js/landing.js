$(document).ready(function(){
    $(window).scroll(function(){
        var top_of_window = $(window).scrollTop();
        var section2 = $('#section-2').offset().top;
        if(top_of_window >= section2-300) {
            $('#nav-icon a').addClass('pull-icon-right');
            $('.navbar-nav').addClass('pull-navmenu-right');
            $('#nav-section-2').addClass('blue-background');
            $('#nav-section-2 a').addClass('white-font');
        } else {
            $('#nav-icon a').removeClass('pull-icon-right');
            $('.navbar-nav').removeClass('pull-navmenu-right');
        }
    });
});