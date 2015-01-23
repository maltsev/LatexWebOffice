$(document).ready(function() {
    $('#scale').validate({
        rules: {
            value: {
                required: false,
				range: [0,1]

            },
		}
    });
});