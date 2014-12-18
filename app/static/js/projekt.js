/*
@author: Thore Thießen
@creation: 04.12.2014 - sprint-nr: 2
@last-change: 18.12.2014 - sprint-nr: 3
*/

// Liste zur Darstellung der Projekte
var projectList;

// initialisiert die Liste für die Projekte, sobald die Seite geladen wurde
$(document).ready(function() {
	projectList = new ListSelector('projekte');
	projectList.setCaptions([
		{'name': 'Name', 'element': 'name'},
		{'name': 'Autor', 'element': 'ownername'},
		{'name': 'Erstellungszeitpunkt', 'element': 'createtime'},
	]);

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

	showProjects();
});

/**
 * Zeigt alle Projekte des Benutzers an.
 */
function showProjects() {
	documentsJsonRequest({
			'command': 'listprojects'
		}, function(result, data) {
			projectList.clearData();
			if (result) {
				// Projekte in die Projektliste eintragen
				for (var i = 0; i < data.response.length; ++i)
					if (i < data.response.length - 1)
						projectList.addData(data.response[i], [], false);
					else
						projectList.addData(data.response[i]);
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
	documentsJsonRequest({
			'command': 'projectrm',
			'id': id
		}, function(result, data) {
			if (result)
				showProjects();
	});
}

/**
 * Erstellt ein neues Projekt.
 * @param name Name des Projektes
 */
function createProject(name) {
	documentsJsonRequest({
			'command': 'projectcreate',
			'name': name
		}, function(result, data) {
			if (result)
				showProjects();
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
