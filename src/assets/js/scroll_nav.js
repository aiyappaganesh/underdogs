$(document).ready(function(){
	$(window).scroll(function(){
                    var top = $('body').scrollTop();
                    if(top <= 0) {
                        $('body').removeClass('scrolled');
                    } else {
                        if(!$('body').hasClass('scrolled')){
                            $('body').addClass('scrolled');
                        }
                    }
                });
});