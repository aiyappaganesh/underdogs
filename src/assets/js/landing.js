$(document).ready(function(){
    $('#section1-carousel').carousel('cycle');
    $('#section4-carousel').carousel('cycle');
    $('#section4-carousel').on('slide.bs.carousel', function(e){
        $(this).find('.stationary').fadeOut(500);
        $('#'+e.relatedTarget.id+'-copy').fadeIn(1000);
    });
});

function set_copy(window_width, window_height) {
    $('.landing-copy').css('margin-top',window_height/2.85);
    $('.landing-copy-big').css('margin-top',window_height/2.85);
    $('.first-content').css('margin-top',window_height/6.5);
}