/*
@author: Thore Thießen
@creation: 04.12.2014 - sprint-nr: 2
@last-change: 11.12.2014 - sprint-nr: 3
*/

var projectList;

// initialisiert die Liste für die Projekte, sobald die Seite geladen wurde
$(document).ready(function() {
	projectList = new ListSelector('projekte');
	projectList.setCaptions([
		{'name': 'Name', 'element': 'name'},
		{'name': 'Autor', 'element': 'author'},
		{'name': 'Erstellungszeitpunkt', 'element': 'created'},
	]);
	showProjects();

	// Projekt öffnen
	projectList.setDClickHandler(openProject);
	$('#open').click(function() {
		if (projectList.getSelected() != null)
			openProject(projectList.getSelected());
		else
			dialogNoSelection('Öffnen');
	});

	// Projekt erstellen
	$('#create').click(function() {
		dialogCreateProject();
	});

	// Projekt löschen
	$('#delete').click(function() {
		if (projectList.getSelected() != null)
			dialogDeleteConfirmation(projectList.getSelected().id);
		else
			dialogNoSelection('Löschen');
	});
	
	// Zip Export von Projekten
	$('#export').click(function() {
		exportZip(projectList.getSelected().id);
	});
});


/*
* Exportiere eine Datei als Zip Datei
*/
function exportZip(id){

jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'exportzip',
			'id': id
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			//Anfrage Fehlerhaft
			console.log({
				'error': 'Fehlerhafte Anfrage: Fehler beim Abrufen der Dateiliste',
				'details': errorThrown,
				'id': id,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success'){
				// Fehler auf dem Server
				console.log({
					'error': 'Fehlerhafte Rückmeldung: Fehler beim Abrufen der Dateiliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			}
			else {
			// Seite neu laden
			alert("test");
			//download file
			
			
		}
		}
	})};
/**
 * Zeigt alle Projekte des Benutzers an.
 */
function showProjects() {
	// Projekte abfragen
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'listprojects'
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			// Fehler beim Laden der Projektliste
			console.log({
				'error': 'Fehler beim Laden der Projektliste',
				'details': errorThrown,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success')
				// Server-seitiger Fehler
				console.log({
					'error': 'Fehler beim Laden der Projektliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			else {
				// Projekte in die Projektliste eintragen
				projectList.clearData();
				for (var i = 0; i < data.response.length; ++i)
					if (i < data.response.length - 1)
						projectList.addData(data.response[i], [], false);
					else
						projectList.addData(data.response[i]);
			}
		}
	});
}

/**
 * Zeigt die Dateiliste für das übergebene Projekt an.
 * @param project Projekt
 */
function openProject(project) {
	document.location.assign('/dateien/#' + project.rootid);
}

/**
 * Löscht ein Projekt.
 * @param id ID des Projektes
 */
function deleteProject(id) {
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'projectrm',
			'id': id
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			// Fehler beim Löschen
			console.log({
				'error': 'Fehler beim Löschen des Projektes',
				'details': errorThrown,
				'id': id,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success')
				// Server-seitiger Fehler
				console.log({
					'error': 'Fehler beim Löschen des Projektes',
					'details': data.response,
					'id': id,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			else
				showProjects();
		}
	});
}

/**
 * Erstellt ein neues Projekt.
 * @param name Name des Projektes
 */
function createProject(name) {
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'projectcreate',
			'name': name
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			// Fehler beim Erstellen
			console.log({
				'error': 'Fehler beim Erstellen des Projektes',
				'details': errorThrown,
				'name': name,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success')
				// Server-seitiger Fehler
				console.log({
					'error': 'Fehler beim Erstellen des Projektes',
					'details': data.response,
					'name': name,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			else
				showProjects();
		}
	});
}

/**
 * Zeigt einen Dialog mit dem Hinweis, dass keine Auswahl getroffen wurde, an.
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
 * Zeigt einen Dialog an, der eine Bestätigung für das Löschen eines Projektes fordert.
 * @param id ID des zu löschenden Projektes
 */
function dialogDeleteConfirmation(id) {
	// Ja-Button
	$('#dialog_deleteConfirmation_yes').click({'id': id}, function(event) {
		deleteProject(event.data.id);
		$('#dialog_deleteConfirmation').dialog('destroy');
	});

	// Nein-Button
	$('#dialog_deleteConfirmation_no').click(function() {
		$('#dialog_deleteConfirmation').dialog('destroy');
	});

	$('#dialog_deleteConfirmation').dialog();
}

/**
 * Zeigt einen Dialog zum Erstellen eines neuen Projektes an.
 */
function dialogCreateProject() {
	// Name zunächst leer
	$('#dialog_createProject_name').val('');

	// OK-Button
	$('#dialog_createProject_ok').click(function() {
		createProject($('#dialog_createProject_name').val());
		$('#dialog_createProject').dialog('destroy');
	});

	$('#dialog_createProject').dialog();
}
