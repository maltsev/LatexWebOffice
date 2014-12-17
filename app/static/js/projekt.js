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
	});
});

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
