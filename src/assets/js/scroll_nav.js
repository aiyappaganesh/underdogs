$(document).ready(function(){
	$(window).scroll(function(){
	                var window_height = $(window).height();
                    var top = $('body').scrollTop();
                    if(top > 120) {
                        $('header').addClass('animate');
                    } else {
                        $('header').removeClass('animate');
                    }
                    if(top < window_height) {
                        $('body').removeClass('scrolled');
                    } else {
                        if(!$('body').hasClass('scrolled')){
                            $('body').addClass('scrolled');
                        }
                    }
                });
});