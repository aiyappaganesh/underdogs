$(document).ready(function(){
    $(window).stellar(
        {
            horizontalOffset: 0,
            verticalOffset: 0
        }
    );
    $(window).scroll(function(){
        var top = $('body').scrollTop();
        if(top <= 0) {
            $('body').removeClass('scrolled');
        } else {
            if(!$('body').hasClass('scrolled')){
                $('body').addClass('scrolled');
            }
        }
        animateBtnArrow($(window).scrollTop()+$(window).height()*0.6);
    });
    animateBtnArrow($(window).scrollTop()+$(window).height()*0.6);
    $('.btn-arrow').click(function(){
        $('html,body').animate({
          scrollTop: $(window).scrollTop()+300
        }, 1000);
        animateBtnArrow(parseFloat($($('.btn-arrow')[0]).css('top').split('px')[0])+300);
    });
});

function animateBtnArrow(scrollTo) {
    $($('.btn-arrow')[0]).animate({
      top: scrollTo
    }, 1, completedBtnArrowAnimate());
}

function completedBtnArrowAnimate() {
    var curr = $($('.btn-arrow')[0]).offset().top;
    var max = $(document).height() - 250;
    if(curr >= max) {
        $($('.btn-arrow')[0]).removeClass('active');
    } else {
        $($('.btn-arrow')[0]).addClass('active');
    }
}