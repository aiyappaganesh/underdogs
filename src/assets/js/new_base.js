$(document).ready(function(){
    set_page_height();
    topArrowDisplay();
    scrollTopArrow();
});

function set_page_height() {
    var window_height = $(window).height();
    var window_width = $(window).width();
    var footer_height = $('.footer').height();
    var min_body_height = window_height-footer_height;
    if(min_body_height > 0) {
        $('.content>.container').css('min-height',min_body_height);
    }
    if(document.getElementsByClassName("fullscreen-section").length > 0) {
        $('.fullscreen-section').css('min-height',window_height);
    }
}


function top_arrow(a){
    "use strict";
    var b=$("#top-arrow");
    b.removeClass("off on");
    if(a==="on"){
        b.addClass("on")
    }else{
        b.addClass("off")
    }
}

function topArrowDisplay(){
    "use strict";
    $(window).scroll(function(){
        var b=$(this).scrollTop();
        var c=$(this).height();
        var d;
        if(b>0){
            d=b+c/2
        }else{
            d=1
        }
        if(d<1e3){
            top_arrow("off")
        }else{
            top_arrow("on")
        }
    })
}

function scrollTopArrow(){
    "use strict";
    $(document).on('click','#top-arrow',function(e){
        e.preventDefault();
        $('body,html').animate({scrollTop:0},$(window).scrollTop()/3,'linear')
    })
}