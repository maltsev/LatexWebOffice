$(document).ready(function() {
    $('#pwrecoverform').validate({
        rules: {
            password1: {
		    required:true,
		    noSpaces:true,
	    },
            password2: {
                required: true,
                equalTo: "#password1"
            }
        },
        messages: {
	    password1: {
		noSpaces: ERROR_MESSAGES.NOSPACESINPASSWORDS
	    },
            password2: {
                equalTo: ERROR_MESSAGES.PASSWORDSDONTMATCH
            },
        },
    });
});
