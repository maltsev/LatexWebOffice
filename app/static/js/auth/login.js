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
