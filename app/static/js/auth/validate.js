// override jquery validate plugin defaults http://stackoverflow.com/a/18754780
$.validator.setDefaults({
    highlight: function(element) {
        $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
	$(element).closest('.reg-input-group').find('span.fa').remove();
    	$(element).closest('.reg-input-group').append('<span class="fa glyphicon glyphicon-remove form-control-feedback" aria-hidden="true"></span>');
    },
    unhighlight: function(element) {
        $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
	$(element).closest('.reg-input-group').find('span.fa').remove();
    	$(element).closest('.reg-input-group').append('<span class="fa glyphicon glyphicon-ok form-control-feedback" aria-hidden="true"></span>');

    },
    errorElement: 'span',
    errorClass: 'help-block',
    errorPlacement: function(error, element) {
        if(element.parent('.input-group').length) {
            error.insertAfter(element.parent());
        } else {
            error.insertAfter(element);
        }
    }
});

jQuery.extend(jQuery.validator.messages, {
	required: ERROR_MESSAGES.NOEMPTYFIELDS,
	email: ERROR_MESSAGES.INVALIDEMAIL,
});
