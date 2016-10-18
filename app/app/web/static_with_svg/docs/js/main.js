( function( $ ) {
	var body    = $( 'body' ),
	    _window = $( window );

	/**
	 * Enables menu toggle for small screens.
	 */
	( function() {
		var nav = $( '#site-navigation' ), button, menu;
		if ( ! nav )
			return;

		button = nav.find( '.menu-toggle' );
		if ( ! button )
			return;

		// Hide button if menu is missing or empty.
		menu = nav.find( '.nav-menu' );
		if ( ! menu || ! menu.children().length ) {
			button.hide();
			return;
		}

		$( '.menu-toggle' ).on( 'click.twentythirteen', function() {
			nav.toggleClass( 'toggled-on' );
		} );
	} )();

	/**
	 * Makes "skip to content" link work correctly in IE9 and Chrome for better
	 * accessibility.
	 *
	 * @link http://www.nczonline.net/blog/2013/01/15/fixing-skip-to-content-links/
	 */
	_window.on( 'hashchange', function() {
		var element = document.getElementById( location.hash.substring( 1 ) );

		if ( element ) {
			if ( ! /^(?:a|select|input|button|textarea)$/i.test( element.tagName ) )
				element.tabIndex = -1;

			element.focus();
		}
	} );

	( function() {
		// Exclude this elements in activating main nav
		$('.menu-toggle').click(function(e){
			e.stopPropagation();
		});
		
		// Hide main nav
		function userMenuHide() {
			$('#site-navigation').removeClass('toggled-on');
		};
		
		// Hide main nav when anywhere on the document is activated
		$(document).click(function(){
			userMenuHide();
		});
		
		// Hide main nav when ESC key is pressed
		$(document).keydown(function(e) {
			if (e.keyCode == 27) {
				userMenuHide();
			}
		});
	} )();
	
	// Check if nav li has children
	$(function () {
		$('.nav-menu > ul > li:has(.children)').addClass('parent-menu');
	});
	
	$(function() {
		var position = $('.navbar').position().top;
		
		$(window).scroll(function() {
			if ($(this).scrollTop() > position) {
				$('.navbar').addClass('sticky');
			} else {
				$('.navbar').removeClass('sticky');
			}
		});
	});
	
	$(function() {
		$(window).scroll(function() {
			if ($(this).scrollTop() > $(window).height()) {
				$('.back-top-link-cr').fadeIn(200);
			} else {
				$('.back-top-link-cr').fadeOut(200);
			}
		});
	});
	
	$(function() {
		$('.back-top-link-cr').click(function() {
			$('body,html').animate({scrollTop:0},400);
		});
	});
	
} )( jQuery );