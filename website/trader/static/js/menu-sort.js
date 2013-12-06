jQuery(function($) {
   $('.module table').sortable({
      items: 'tr',
        handle: 'td.original',
	stop: function(event, ui) {
	   var ids = new Array();
	   $('input[type="hidden"]', '.module table').each(function(i, e) {
	      if ($(this).attr('name').search(/photo_set-\d+-id/) > -1)
		if ($(this).val())
		  ids.push($(this).val());
	   });
	   $.ajax({
	      url: $('form#reorder_product_photos').attr('action'),
	      type: "POST",
	      data: {ids:ids},
	      
	      success: function() {
	       
	      }, 
	   });
	},
      
   });
   $('td.original', '.module').css('cursor', 'move');
   $('td.original p', '.module').append(jQuery('<img/>').attr('src','/static/images/updown.png').css('padding-left','5px'));
   $('.module table').find('input[id$=order]').parent('td').hide();
   $('.module table thead th:eq(2)').hide()
});
