$(window).scroll(function() {
	if ($(this).scrollTop() > 230) {
		$('nav').addClass("sticky");
	}
	else {
		$('nav').removeClass("sticky");		
	}
});