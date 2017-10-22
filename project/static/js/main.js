function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

// Search
function searchToggle(obj, evt){
	var container = $(obj).closest('.search-wrapper');
	if(!container.hasClass('active')){
		  container.addClass('active');
		  evt.preventDefault();
	}
	else if(container.hasClass('active') && $(obj).closest('.input-holder').length == 0){
		  container.removeClass('active');
		  // clear input
		  container.find('.search-input').val('');
		  // clear and hide result container when we press close
		  container.find('.result-container').fadeOut(100, function(){$(this).empty();});
	}
}
function submitFn(obj, evt){
	value = $(obj).find('.search-input').val().trim();
	$(obj).find('.result-container').fadeIn(100);
	evt.preventDefault();
}

$( document ).ready(function() {
    try {
        window.$ = window.jQuery = require('jquery');
        window.Popper = require('popper.js').default;
        require('bootstrap');
    } catch (e) {}
});