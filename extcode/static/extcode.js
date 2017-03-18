//  sphinxcontrib.extcode
//  ~~~~~~~~~~~~~~~~~~~~~~
//
//  This package is a namespace package that contains all extensions
//  distributed in the ``sphinx-contrib`` distribution.
//
//  :copyright: Copyright 2007-2013 by the Sphinx team, see AUTHORS.
//  :license: BSD, see LICENSE for details.

$(function(){
	$('.extcode').each(function(i, elem){
		elem = $(elem);
		if (elem.hasClass('extcode-layout-toggle')) {
			var hover = $('<span>').addClass('extcode-hover').text('rst');
			hover.click(function(evt){
				console.log(evt);
				elem.find('.highlight-rst').toggle();
				elem.find('.extcode-rendered').toggle();
				elem.find('.extcode-overlay').toggle();
				evt.stopPropagation();
				return false;
			});
			elem.append(hover);
		}
	});
});
