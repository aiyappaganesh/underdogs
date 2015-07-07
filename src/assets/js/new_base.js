$(document).ready(function(){
    set_page_height();
    topArrowDisplay();
    scrollTopArrow();
    $('.centered-full-screen-element').height($(window).height());
    $('.centered-full-screen-element').width($(window).width());
    $('.centered-full-width-element').width($(window).width());
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

function displayPhotoThumbnail(e) {
    console.log('Reached displayPhotoThumbnail for: '+e);
    var photo_files = e.files;
    var photo_file = photo_files[0];

    if (!photo_file.type.match('image.*')) {
        alert('Not an image file');
        $('#photo').focus();
        return;
    }

    var file_reader = new FileReader();
    file_reader.onload = (function(photo) {
      return function(ev) {
        $('#photo-holder').attr('src', ev.target.result);
        $('#photo-holder').attr('title', photo.name);
      };
    })(photo_file);

    file_reader.readAsDataURL(photo_file);
}