/*
@author: Thore Thießen, Timo Dümke
@creation: 21.11.2014 - sprint-nr: 2
@last-change: 25.11.2014 - sprint-nr: 2
*/

/// Editor
var editor;

/**
 * Lädt den ACE-Editor, sobald das Dokument vollständig geladen wurde.
 */
$(document).ready(function() {
	editor = ace.edit('editor');

	// Clouds-Theme
	editor.setTheme('ace/theme/clouds');

	// Latex-Modus
	editor.getSession().setMode('ace/mode/latex');
	// TODO: ACE-BasicAutoCompletion?

	// automatisches Setzen von Klammern
	editor.on('change', autoBraceCompletion);

	// TODO: automatische Vervollständigung von Blöcken (\begin{…} … \end{…})
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
				// Datei in den Editor laden
				editor.setValue(response.responseText, 0);
			} else {
				// Fehler bei der Anfrage
				// TODO: Client umleiten?

				// DEBUG
				console.log({
					'error': 'Fehler beim Laden der Datei',
					'id': id,
					'statusCode': response.status,
					'statusText': response.statusText
				});
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
