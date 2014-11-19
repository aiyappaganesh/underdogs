$(document).ready(function(){
    set_page_height();
});

$(document).ready(function(){
    $(window).resize(function(){
        set_page_height();
    });
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

function set_page_height() {
    var window_height = $(window).height();
    $('.landing-section').height(window_height);
    $('.landing-copy').css('margin-top',window_height/2);
}