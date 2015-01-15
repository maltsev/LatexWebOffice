/*
@author: Thore Thießen, Timo Dümke, Franziska Everinghoff
@creation: 21.11.2014 - sprint-nr: 2
@last-change: 18.12.2014 - sprint-nr: 3
*/

/// ID der im Editor geöffneten Datei
var id;

/// Editor
var editor;

/// Änderungen im Editor gespeichert?
var changesSaved = true;
	
/**
 * Lädt den Editor, sobald das Dokument vollständig geladen wurde.
 */
$(document).ready(function() {
	
	// Datei-ID abfragen
	id = parseInt(location.hash.substr(1));
	if (isNaN(id))
		// ungültige ID
		backToProject();
	else {
		// ACE-Editor laden
		editor = ace.edit('editor');
		editor.setTheme('ace/theme/clouds');
		editor.getSession().setMode('ace/mode/latex');
		editor.getSession().setUseWrapMode(true);
		editor.setOptions({'enableBasicAutocompletion': true});
		
		// Vertikale Zeichenbegrenzung (80 Zeichen) ausgeblendet	
		editor.setShowPrintMargin(false);

		// automatisches Setzen von Klammern
		editor.on('change', autoBraceCompletion);

		// TODO: automatische Vervollständigung von Blöcken (\begin{…} … \end{…})

		// Speicheraufforderung bei ungespeicherten Änderungen
		editor.on('change', function() {
			changesSaved = false;
		});
		$(window).bind('beforeunload', function() {
			if (!changesSaved)
				return('Ungespeicherte Änderungen, wollen Sie den Editor wirklich verlassen?');
		});

		// Button für das Speichern belegen
		$('#save').click(function() {
			saveFile(id);
		});

		// Button für das Kompilieren belegen
		$('#compile').click(function() {
			compile(id);
		});
		
		loadFile(id);
	}
});

// Dialogfenster Editor zurück
function confirmExit() {
	saveFile(id);
	$('#dialog_editor_verlassen').dialog();
}

// Dialogfenster Tabellenassistent
function createTable() {
	$('#dialog_tabelle_erstellen').dialog();
}

function insertImage(){
	var folderid;
	//get folder id
	documentsJsonRequest({
			'command': 'fileinfo',
			'id': id,
		}, function(result, data) {
			if (result)
			{
				getFiles(data.response.folderid);
			}
	});

}
var filelist = [];
function getFiles(folderid){
	filelist.push("");
	documentsJsonRequest({
			'command': 'listfiles',
			'id': folderid,
		}, function(result, data) {
			if (result)
			{
				var arr = data.response.files;

				for(var i=0;i<arr.length;i++){
					var obj = arr[i];
					if(obj.mimetype.indexOf("image") > -1){
						filelist.push(obj.name);
					};
				}
				generateFileSelection();
			}
	});
}

function generateFileSelection(){
	var myDiv = document.getElementById("selectionList");
	
	//Create and append select list
	var selectList = document.createElement("select");
	selectList.id = "mySelect";
	selectList.onchange = function () {
		includeSelectedFile(this);
	};
	myDiv.appendChild(selectList);

	//Create and append the options
	for (var i = 0; i < filelist.length; i++) {
		var option = document.createElement("option");
		option.value = filelist[i];
		option.text = filelist[i];
		selectList.appendChild(option);
	}
}
function includeSelectedFile(a){
	editor.insert("\\includegraphics[width=0.7\\textwidth]{"+a.value+"}");
}

function includeImagePath(id){
		documentsJsonRequest({
			'command': 'fileinfo',
			'id': id,
		}, function(result, data) {
			if (result)
			{
				editor.setValue("\\includegraphics[width=0.7\\textwidth]{"+data.response.filename+"}", 0);
				//editor.getSelection().selectTo(0, 0);
			}
	});
}

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
	// TODO: auf das richtige Projekt verweisen
	window.location.replace('/projekt/');
}

/**
 * Lädt eine Datei in den Editor.
 * @param id ID der Datei
 */
function loadFile(id) {
	documentsDataRequest({
			'command': 'downloadfile',
			'id': id
		}, function(result, data) {
			if (result) {
				editor.setValue(data, 0);
				editor.getSelection().selectTo(0, 0);
				changesSaved = true;
			} else
				backToProject();
	});
}

/**
 * Speichert den Inhalt aus dem Editor in eine Datei.
 * @param id ID der Datei
 */
function saveFile(id) {
	documentsJsonRequest({
			'command': 'updatefile',
			'id': id,
			'content': editor.getValue()
		}, function(result, data) {
			if (result)
				changesSaved = true;
	});
}

/**
 * Kompiliert eine Datei und zeigt die PDF an.
 * @param id ID der Datei
 */
function compile(id) {
	// TODO: parallele Anzeige TEX/PDF implementieren

	documentsJsonRequest({
			'command': 'compile',
			'id': id
		}, function(result, data) {
			if (result)
				documentsRedirect({
					'command': 'downloadfile', 
					'id': data.response.id
				});
	});
}
