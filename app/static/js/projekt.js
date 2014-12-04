/*
@author: Thore Thießen
@creation: 04.12.2014 - sprint-nr: 2
@last-change: 04.12.2014 - sprint-nr: 2
*/

// TODO: Funktionen generell überarbeiten/restrukturieren

$(document).ready(function() {
	displayProjects();
});

// zeigt alle Projekte an
function displayProjects() {
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
			// Fehler beim Speichern
			console.log({
				'error': 'Fehler beim Laden der Projekte',
				'details': errorThrown,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success')
				// Server-seitiger Fehler
				console.log({
					'error': 'Fehler beim Laden der Projekte',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			else {
				var projectList = '<h1>Projekte</h1>';
				$.each(data.response, function(index, value) {
					projectList += '<a onclick="displayProjectFiles(' + value.id + ', \'' + 
							htmlEscape(value.name) + '\')">' +  value.name + '</a><br />';
				});
				projectList += '<form onsubmit="createProject()"><input type="text" ' + 
						'id="projektName" /><input type="submit" value="Projekt erstellen" ' + 
						'/></form>';
				$('#projekte').html(projectList);
			}
		}
	});
}

function createProject() {
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'projectcreate',
			'name': $('#projektName').val()
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			// Fehler beim Speichern
			console.log({
				'error': 'Fehler beim Erstellen des Projektes',
				'details': errorThrown,
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
					'statusCode': response.status,
					'statusText': response.statusText
				});
			else
				displayProjects();
		}
	});

	return(false);
}

// zeigt die Dateien eines Projektes an
function displayProjectFiles(id, name) {
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'listfiles',
			'id': id
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			// Fehler beim Speichern
			console.log({
				'error': 'Fehler beim Laden der Dateiliste',
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
					'error': 'Fehler beim Laden der Dateiliste',
					'details': data.response,
					'id': id,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			else {
				var fileList = '<h1>Dateien für ' + htmlEscape(name) + '</h1>';
				fileList += folderList(data.response, '');
				$('#dateien').html(fileList);
			}
		}
	});
}

// HTML-Liste der Dateien
function folderList(object, path) {
	var html = '';

	// Dateien auflisten
	// TODO: Endungserkennung ist scheiße
	$.each(object.files, function(index, value) {
		if (value.name.indexOf('.tex', value.name.length - 4) !== -1)
			html += '<a href="/editor/?id=' + value.id + '">' + path + '/' + value.name + 
					'</a><br />';
		else
			html += path + '/' + value.name + '<br />';
	});

	// Ordner auflisten
	$.each(object.folders, function(index, value) {
		html += folderList(value, path + '/' + value.name);
	});

	return(html);
}
