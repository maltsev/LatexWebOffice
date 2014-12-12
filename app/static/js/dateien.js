/*
@author: Timo Dümke
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 12.12.2014 - sprint-nr: 3
*/
var filelistHandler;
$( document ).ready(function() {
filelistHandler = new ListSelector("dateien");
filelistHandler.setCaptions([
{'name': 'Name', 'element': 'name'},
{'name': 'Dateityp', 'element': 'filetype'}
]);
showFilelist(1);
});

function showFilelist(projectID){
jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'listfiles',
			'id': projectID
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			//Anfrage Fehlerhaft
			console.log({
				'error': 'Fehler beim Abrufen der Dateiliste',
				'details': errorThrown,
				'id': projectID,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success'){
				// Fehler auf dem Server
				console.log({
					'error': 'Fehler beim Abrufen der Dateiliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			}
			else {
			// vorhandene Dateiliste entfernen
			filelistHandler.clearData();
			alert(data.response[2]);
			
			
		}
		}
	});
}



