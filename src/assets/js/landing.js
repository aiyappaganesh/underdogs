$(document).ready(function(){
    $('#section1-carousel').carousel('cycle');
});

$(document).ready(function(){
    $(window).scroll(function(){
        var top_of_window = $(window).scrollTop();
        var section2 = $('#section-2').offset().top;
        if(top_of_window >= section2-($(window).height()/2)) {
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

function set_copy(window_width, window_height) {
    $('.landing-copy').css('margin-top',window_height/2.85);
    $('.landing-copy-big').css('margin-top',window_height/2.85);
    $('.first-content').css('margin-top',window_height/6.5);
}