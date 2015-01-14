$(document).ready(function() {
    $('#regform').validate({
        rules: {
            first_name: {
                required: true,
                pattern: /[\s]*$/,
            },
            email: {
                required: true,
                email: true,
                remote: {
                    url: "/reguserexists/",
                    type: "post",
                    data: {
                        'email': function() {
                            return $('#email').val();
                        }
                    }

                },
            },
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
            first_name: {
                pattern: ERROR_MESSAGES.INVALIDCHARACTERINFIRSTNAME
            },
	    password1: {
		noSpaces: ERROR_MESSAGES.NOSPACESINPASSWORDS
	    },
            password2: {
                equalTo: ERROR_MESSAGES.PASSWORDSDONTMATCH
            },
            email: {
                remote: ERROR_MESSAGES.EMAILALREADYEXISTS,
            }
        },
    });
});
