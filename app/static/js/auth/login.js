$(document).ready(function() {
    $('#loginform').validate({
        rules: {
            email: {
                required: true,
                email: true,
            },
            password: "required",
        }
    });
});
$(document).ready(function() {
    $('#password-lost-form').validate({
        rules: {
            email: {
                required: true,
                email: true,
            },
        }
    });
});

