/*
@author: Thore Thießen, Timo Dümke
@creation: 21.11.2014 - sprint-nr: 2
@last-change: 25.11.2014 - sprint-nr: 2
*/

/// ID der im Editor geöffneten Datei
var id;

/// Editor
var editor;

/**
 * Lädt den Editor, sobald das Dokument vollständig geladen wurde.
 */
$(document).ready(function() {
	// Datei-ID abfragen
	id = parseInt($(document).getUrlParam('id'), 10);
	if (isNaN(id))
		// ungültige ID
		backToProject();
	else {
		// ACE-Editor laden
		editor = ace.edit('editor');

		// Clouds-Theme
		editor.setTheme('ace/theme/clouds');

		// Latex-Modus
		editor.getSession().setMode('ace/mode/latex');

		// automatisches Setzen von Klammern
		editor.on('change', autoBraceCompletion);

		// TODO: automatische Vervollständigung von Blöcken (\begin{…} … \end{…})

		// Button für das Speichern belegen
		$('#save').click(function() {
			saveFile(id);
		});

		// Dokument laden
		loadFile(id);
	}
});

/// Klammern, welche automatisch geschlossen werden sollen
var braces = {
	'{': '}',
	'[': ']'
}

/**
 * Fügt automatisch die schließende zu einer eingegebenen öffnenden Klammer ein.
 * @param e Event
 */
function autoBraceCompletion(e) {
	if (e.data.action == 'insertText') {
		var pos = editor.getSelection().getCursor();
		if (e.data.text in braces && 
				editor.getSession().getLine(pos.row).charAt(pos.column - 1) != '\\') {
			// schließende Klammer zu einer eingegebenen öffnenden hinzufügen
			editor.moveCursorTo(pos.row, pos.column + 1);
			editor.insert(braces[e.data.text]);
			editor.moveCursorToPosition(pos);
		}
	}
}

/**
 * Leitet den Benutzer zurück zur Projektverwaltung.
 */
function backToProject() {
	// TODO: auf das richtige Projekt verweisen?
	// FIXME: Adresse für die Projektverwaltung eingeben
	window.location.replace('/');
}

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
		'error': function(response, textStatus, errorThrown) {
			// Fehler bei der Anfrage
			console.log({
				'error': 'Fehler beim Laden der Datei',
				'details': errorThrown,
				'id': id,
				'statusCode': response.status,
				'statusText': response.statusText
			});
			backToProject();
		},
		'success': function(data, textStatus, response) {
			// Datei erfolgreich geladen
			editor.setValue(data, 0);
			editor.getSelection().selectTo(0, 0);
			// TODO: Editor-Funktionen entsperren
		}
	});
}

/**
 * Speichert den Inhalt aus dem Editor in eine Datei.
 * @param id ID der Datei
 */
function saveFile(id) {
	// TODO: Editor-Funktionen sperren

	// Dokument schicken
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'updatefile',
			'id': id,
			'content': editor.getValue()
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			// Fehler beim Speichern
			console.log({
				'error': 'Fehler beim Speichern der Datei',
				'details': errorThrown,
				'id': id,
				'statusCode': response.status,
				'statusText': response.statusText
			});
			// TODO: Editor-Funktionen entsperren
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success')
				// Server-seitiger Fehler
				console.log({
					'error': 'Fehler beim Speichern der Datei',
					'details': data.response,
					'id': id,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			// TODO: Editor-Funktionen entsperren
		}
	});
}
