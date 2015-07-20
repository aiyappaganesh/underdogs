$(document).ready(function(){
    $('#section1-carousel').carousel('cycle');
    $('#section4-carousel').on('slide.bs.carousel', function(e){
        changeCarouselCopy(this, e);
    });
    $('#track').on('slide.bs.carousel', function(e){
        changeCarouselCopy(this, e);
    });
});

function changeCarouselCopy(element, event) {
    $(element).find('.carousel-copy').fadeOut(500);
    $('#'+event.relatedTarget.id+'-copy').fadeIn(1000);
}