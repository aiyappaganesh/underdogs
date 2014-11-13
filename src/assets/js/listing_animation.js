$(document).ready(function(){
    animate_list();
});

$(document).ready(function(){
    $(window).scroll(function(){
        animate_list();
    });
});

function animate_list() {
    var top_of_window = $(window).scrollTop();
    var window_height = $(window).height();
    var bottom_of_window = top_of_window + window_height;
    $('.original-pos').each(function(i, v){
        var row_pos = $(this).offset().top;
        $(this).css('transition-duration',((i+1)*0.5)+'s');
        if(bottom_of_window > row_pos) {
            $(this).removeClass('original-pos');
            $(this).addClass('new-pos');
        }
    });
    $('.new-pos').each(function(i, v){
        var row_pos = $(this).offset().top;
        if(bottom_of_window < row_pos+50) {
            $(this).css('transition-duration',((i+1)*0.05)+'s');
            $(this).removeClass('new-pos');
            $(this).addClass('original-pos');
        }
    });
}