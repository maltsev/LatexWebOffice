/*
@author: Ingolf Bracht
@creation: 14.12.2014 - sprint-nr: 3
@last-change: 14.12.2014 - sprint-nr: 3
*/

var templatesList;

/*
 * Initialisiert die Liste für die Vorlagen, sobald die Seite geladen wurde
 */
$(document).ready(function() {
	
	templatesList = new ListSelector('vorlagen');
	templatesList.setCaptions([
		{'name': 'Name', 'element': 'name'},
		{'name': 'Autor', 'element': 'ownername'},
		{'name': 'Erstellungszeitpunkt', 'element': 'createtime'}
	]);
	showTemplates();
	
	// Menü-Eintrag für das Umwandeln belegen
	$('#import').click(function() {
		
		if(templatesList.getSelected()!=null)
			dialogTemplateToProject(templatesList.getSelected().id);
		else
			dialogNoSelection('Importieren');
	});
});

/**
 * Listet die Vorlagen des Benutzers auf.
 */
function showTemplates() {
	
	// Vorlagen abfragen
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'listtemplates'
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response,textStatus,errorThrown) {
			// Fehler beim Laden der Vorlagen-Liste
			console.log({
				'error': 'Fehler beim Laden der Vorlagen-Liste',
				'details': errorThrown,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data,textStatus,response) {
			if(data.status!='success')
				// Server-seitiger Fehler
				console.log({
					'error': 'Fehler beim Laden der Vorlagen-Liste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			else {
				// Vorlagen in die Vorlagen-Liste eintragen
				templatesList.clearData();
				for(var i=0;i<data.response.length;++i)
					if(i<data.response.length-1)
						templatesList.addData(data.response[i],[],false);
					else
						templatesList.addData(data.response[i]);
			}
		}
	});
}

/*
 * Wandelt eine Vorlage in ein Projekt um.
 *
 * @param id ID der Vorlage, aus welcher ein Projekt erzeugt werden soll
 * @param name Name des zu erzeugenden Projektes
 */
function templateToProject(id,name) {
	
	// Vorlage in Projekt umwandeln
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'template2project',
			'id': id,
			'name': name
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			// Fehler beim Aufruf
			console.log({
				'error': 'Fehler beim Importieren',
				'details': errorThrown,
				'id': id,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success') {
				// Server-seitiger Fehler
				console.log({
					'error': 'Fehler beim Importieren',
					'details': data.response,
					'id': id,
					'statusCode': response.status,
					'statusText': response.statusText
				});
				alert('Fehler beim Importieren'+'\n'+data.response);
			}
			else
				// Weiterleitung zum erzeugten Projekt
				document.location.assign('/dateien/#'+response.id);
		}
	});
}

/**
 * Zeigt einen Dialog mit dem Hinweis, dass keine Auswahl getroffen wurde, an.
 *
 * @param method Name der Funktion, die eine Auswahl benötigt
 */
function dialogNoSelection(method) {
	
	// Funktion
	$('#dialog_noSelection_method').text(method);
	
	// OK-Button
	$('#dialog_noSelection_ok').click(function() {
		$('#dialog_noSelection').dialog('destroy');
	});
	
	$('#dialog_noSelection').dialog();
}

/**
 * Zeigt einen Dialog zum Erstellen eines neuen Projektes aus einer Vorlage an.
 *
 * @param id ID der Vorlage, aus welcher ein Projekt erzeugt werden soll
 */
function dialogImportToProject(id) {
	
	// Name zunächst leer
	$('#dialog_importToProject_name').val('');

	// OK-Button
	$('#dialog_importToProject_ok').click(function() {
		template2project(id,$('#dialog_importToProject_name').val());
		$('#dialog_importToProject').dialog('destroy');
	});

	$('#dialog_importToProject').dialog();
}