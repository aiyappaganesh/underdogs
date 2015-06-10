$(document).ready(function(){
    set_page_height();
});

function set_page_height() {
    var window_height = $(window).height();
    var window_width = $(window).width();
    if(document.getElementsByClassName("fullscreen-section").length > 0) {
        $('.fullscreen-section').css('min-height',window_height);
    }
    set_copy(window_width, window_height);
}