// überprüft, ob die beiden bei der Registrierung angegebenen Passwörter übereinstimmen
function matchPasswords(event) {
	if (document.getElementById('password1').value == document.getElementById('password2').value)
		document.getElementById('password2').setCustomValidity('');
	else
		document.getElementById('password2').setCustomValidity(ERROR_MESSAGES.PASSWORDSDONTMATCH);
}
$(document).ready(function() {
	if (document.getElementById('password1') && document.getElementById('password2')) {
		document.getElementById('password1').addEventListener("input", matchPasswords);
		document.getElementById('password2').addEventListener("input", matchPasswords);
	}
});
