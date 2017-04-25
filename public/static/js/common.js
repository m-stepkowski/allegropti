
	function form_post(elem){
		par_post = elem.form;
		elem.disabled=true;
		elem.parentElement.innerHTML='<i class="fa fa-spinner fa-spin"></i>';
		par_post.submit();
	}
