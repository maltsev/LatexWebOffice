/*
@author: Munzir Mohamed, Thore Thießen
@creation: 07.11.2014 - sprint-nr: 1
@last-change: 13.11.2014 - sprint-nr: 1
*/

// überprüft, ob die beiden bei der Registrierung angegebenen Passwörter übereinstimmen
function matchPasswords(event) {
	if ($('#password1').val() == $('#password2').val())
		$('#password2')[0].setCustomValidity('');
	else
		$('#password2')[0].setCustomValidity(ERROR_MESSAGES.PASSWORDSDONTMATCH);
}
$(document).ready(function() {
	if ($('#password1').length && $('#password2').length) {
		$('#password1').change(matchPasswords);
		$('#password2').change(matchPasswords);
	}
});
