// Überprüft Formular-Daten und zeigt ggf. entsprechende Fehlermeldungen an
function validateForm(id) {
	// Eingabefelder des Formulars einlesen
	var formElements = document.getElementById(id).getElementsByTagName('input');

	// Werte der Eingabefelder überprüfen
	for (var i = 0; i < formElements.length; ++i) {
		var element = formElements[i];

		// eMail-Adresse
		if (element.type == 'email') {
			if (!/(.+)@(.+){2,}\.(.+){2,}/.test(element.value))
				element.setCustomValidity('Bitte eine gültige eMail-Adresse angeben');
			else
				element.setCustomValidity('');
		}
	}

	// TODO: nur submit-Buttons finden
	document.getElementById(id).getElementsByTagName('button')[0].click();

	return(false);
}