/*
@author: Thore Thießen
@creation: 21.11.2014 - sprint-nr: 2
@last-change: 24.11.2014 - sprint-nr: 2
*/

/**
 * Lädt eine Datei in den Editor.
 * @param id ID der Datei
 */
function loadFile(id) {
	// TODO: Editor-Funktionen sperren

	// Dokument abfragen
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'downloadfile',
			'id': id
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'text',
		'complete': function(response, status) {
			if (status == 'success') {
				$('#editor').html(response.responseText);
				// TODO: Datei in den Editor laden
			} else {
				// Fehler bei der Anfrage
				alert('Fehler: ' + status);
				// TODO: Client umleiten?
			}

			// TODO: Editor-Funktionen entsperren
		}
	});
}

/**
 * Speichert den Inhalt aus dem Editor in eine Datei.
 * @param id ID der Datei
 */
function saveFile(id) {
	// TODO: implementieren
}
