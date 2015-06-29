$(document).ready(function(){
    $('#section1-carousel').carousel('cycle');
    $('#section4-carousel').on('slide.bs.carousel', function(e){
        $(this).find('.stationary').fadeOut(500);
        $('#'+e.relatedTarget.id+'-copy').fadeIn(1000);
    });
    $('#track').on('slide.bs.carousel', function(e){
        $(this).find('.stationary').fadeOut(500);
        $('#'+e.relatedTarget.id+'-copy').fadeIn(1000);
    });
});