$(document).ready(function(){
    $('#section1-carousel').carousel('cycle');
});

function set_copy(window_width, window_height) {
    $('.startups-copy').css('margin-top',window_height/2.5);
    if(window_width < 1280) {
        var font_size = (window_width*48)/1280;
        var line_height = (window_width*72)/1280;
        $('.startups-copy').css('font-size',font_size);
        $('.startups-copy').css('line-height',line_height+'px');
    }
}