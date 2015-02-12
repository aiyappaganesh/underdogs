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
    $('.landing-copy').css('margin-top',window_height/2.5);
    if(window_width < 1280) {
        var font_size = (window_width*48)/1280;
        var line_height = (window_width*72)/1280;
        $('.landing-copy').css('font-size',font_size);
        $('.landing-copy').css('line-height',line_height+'px');
    }
}