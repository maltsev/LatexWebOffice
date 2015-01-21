/**
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *      Temporäre Datei
 *
 *      Vorlagen und Projekte sind fast gleich, deshalb wäre es besser
 *      projekt.js für die Seite mit den Vorlagen anpassen und nicht eine neue
 *      copy-paste Datei vorlagen.js erstellen.
 *
 *      Die template2project Funktion kann man hier schreiben oder in projekt.js
 *
 *      Kirill Maltsev
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
 *
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