$(document).ready(function() {
    $('#regform').validate({
        rules: {
            first_name: {
                required: true,
                pattern: /^[a-zA-zÄÖÜäöü]*$/,
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

                }

            },
            password1: "required",
            password2: {
                required: true,
                equalTo: "#password1"
            }
        },
        messages: {
            first_name: {
                pattern: ERROR_MESSAGES.INVALIDCHARACTERINFIRSTNAME
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
