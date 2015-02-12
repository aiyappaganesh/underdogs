$(document).ready(function(){
    set_page_height();
});

$(document).ready(function(){
    $(window).resize(function(){
        set_page_height();
    });
});

function set_page_height() {
    var window_height = $(window).height();
    var window_width = $(window).width();
    if(document.getElementsByClassName("fullscreen-section").length > 0) {
        $('.fullscreen-section').height(window_height);
    }
    set_copy(window_width, window_height);
}