/*
@author: Ingolf Bracht
@creation: 14.12.2014 - sprint-nr: 3
@last-change: 14.12.2014 - sprint-nr: 3
*/

var templatesList;

/*
 * Initialisiert die Liste für die Vorlagen, sobald die Seite geladen wurde.
 */
$(document).ready(function() {
	
	templatesList = new ListSelector('vorlagen');
	templatesList.setCaptions([
		{'name': 'Name', 'element': 'name'},
		{'name': 'Autor', 'element': 'ownername'},
		{'name': 'Erstellungszeitpunkt', 'element': 'createtime'}
	]);
	
	// Projekt-Export
	$('#export').click(function() {
		
		if(templatesList.getSelected()!=null)
			dialogTemplateToProject(templatesList.getSelected().id);
		else
			dialogNoSelection('Exportieren');
	});
	
	showTemplates();
});

/**
 * Listet die Vorlagen des Benutzers auf.
 */
function showTemplates() {

	documentsJsonRequest({
		'command': 'listtemplates'
		},
		function(result,data) {
			templatesList.clearData();
			if(result) {
				// Vorlagen in die Vorlagen-Liste eintragen
				for (var i=0;i<data.response.length;++i)
					if(i<data.response.length-1)
						templatesList.addData(data.response[i],[],false);
					else
						templatesList.addData(data.response[i]);
			}
	});
}

/*
 * Wandelt eine Vorlage in ein Projekt um und leitet zu dessen Datei-Liste weiter.
 *
 * @param id ID der Vorlage, aus welcher ein Projekt erzeugt werden soll
 * @param name Name des zu erzeugenden Projektes
 * @param handler Funktion mit function(bool result, msg), die nach der Operation aufgerufen wird
 */
function templateToProject(id,name,handler) {

	documentsJsonRequest({
		'command': 'template2project',
		'id': id,
		'name': name
		},
		function(result,data) {
			if(result) {
				// Weiterleitung zum erzeugten Projekt
				document.location.assign('/dateien/#'+data.response.rootid);
				handler(true,'');
			} else
				handler(false,data.response);
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
	
	// öffnet die Dialogbox
	$('#dialog_noSelection').dialog();
}

/**
 * Zeigt einen Dialog zum Erstellen eines neuen Projektes aus einer Vorlage an.
 *
 * @param id ID der Vorlage, aus welcher ein Projekt erzeugt werden soll
 */
function dialogTemplateToProject(id) {
	
	// leert das Eingabefeld für den Projektnamen
	$('#dialog_templateToProject_name').val('');
	
	// setzt die Fehlermeldung zurück
	$('#dialog_templateToProject_message').text('');
	if(!$('#dialog_templateToProject_message').hasClass('invisible'))
		$('#dialog_templateToProject_message').addClass('invisible');
	
	// OK-Button
	$('#dialog_templateToProject_ok').click(function() {
		templateToProject(id,$('#dialog_templateToProject_name').val(),function(result,msg) {
			if(result)
				$('#dialog_templateToProject').dialog('destroy');
			else {
				$('#dialog_templateToProject_message').text(msg);
				$('#dialog_templateToProject_message').removeClass('invisible');
			}
		});
	});
	
	// öffnet die Dialogbox
	$('#dialog_templateToProject').dialog();
}