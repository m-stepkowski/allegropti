
	$('#but_item_search').click(function(){
	this.form.submit();
	this.disabled=true;
	this.innerHTML='<i class="fa fa-spinner fa-spin"></i>';
	});
