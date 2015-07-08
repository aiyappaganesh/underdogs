$(document).ready(function(){
    $(window).scroll(function(){
        var scroll_window_top = $(window).scrollTop();
        //var scroll_window_bottom = scroll_window_top + $(window).height();
        var scroll_window_upper_middle = scroll_window_top + ($(window).height()/4);
        var scroll_window_lower_middle = scroll_window_top + (3*($(window).height()/4));
        $('.scrollable li').each(function(){
            var li_top = $(this).offset().top;
            var li_bottom = li_top + $(this).height();
            if(li_top < scroll_window_upper_middle || li_bottom > scroll_window_lower_middle) {
                $(this).removeClass('focus');
            } else {
                $(this).addClass('focus');
            }
        });
    });
});