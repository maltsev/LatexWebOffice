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
	
/// Grafikassistentdropdownmenue
var dropdownWindow = false;

/// Grafikassistent Selectionid
var selectionid = 0;

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
		editor.setOptions({'enableBasicAutocompletion': true,autoScrollEditorIntoView: true});
		
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
		$('.ace_scroller').on('scroll', function () {
			$('.ace_gutter').scrollTop($(this).scrollTop());
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
	$('#dialog_tabelle_erstellen').dialog({
	width:'auto'});
}

// Dialogfenster Grafikassistent
function openInsertImageDialog() {
	$('#dialog_grafik_einfuegen').dialog({
	width:'auto'});
}

// Klammern, welche automatisch geschlossen werden sollen
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

/**
 * liest die Tabelle aus und fügt sie in das Textfeld des Editors ein
 */

function table_readout_input() {
	var header = "";
	for (var i =  0; i < hot.countCols();i++)
		header += "l";
		
	var fulltable = "";
		for (var j = 0; j < hot.countRows()-1;j++)
		{
			var rowcontent = "";
			for (var i =  0; i < hot.countCols()-1;i++)
				rowcontent += hot.getDataAtCell(j,i)+"&";
				rowcontent += hot.getDataAtCell(j,i++)+"\\\\"
				fulltable += rowcontent +"\n";
		}
		editor = ace.edit('editor');
		editor.insert("\\begin{table}[h]\n" + "\\begin{tabular}{"+header+"}\n "
		+ fulltable+"\\end{tabular}\n"+"\\end{table}\n");
}

/**
* Baumstruktur mittels JSTree erstellen
*/
var tree = null;

$(function () {
	// ausgewählter Knoten
	var selectedNode = null;

    // ID zum vorliegenden Projekt
	var rootFolderId = parseInt(location.hash.substr(1), 10);
	createJSTree();
	function createJSTree(){
		//get folder id
		documentsJsonRequest({
				'command': 'fileinfo',
				'id': rootFolderId,
			}, function(result, data) {
				if (result)
				{
					rootFolderId = data.response.folderid;
					reloadProject();
				}
		});
	}
	
    function reloadProject() {
        documentsJsonRequest({command: "listfiles", id: rootFolderId}, function(result, data) {
            if (! result) {
                alert(ERROR_MESSAGES.PROJECTNOTEXIST);
                return;
            }
            renderProject(data.response);
        });
    }


    // folder: {icon: "glyphicon glyphicon-folder-open"},
    // emptyFolder: {icon: "glyphicon glyphicon-folder-close"},
    // file: {icon: "glyphicon glyphicon-file"},
    // pdf: {icon: "glyphicon glyphicon-book"}

    
    function renderProject(data) {
        var jsTreeData = convertRawDataToJsTreeData(data);

        if (tree) {
            tree.jstree(true).settings.core.data = jsTreeData;
            tree.jstree(true).refresh();
            return;
        }

        tree = $(".fileswrapper").jstree({
            core: {
                check_callback: true,
                multiple: true,
                data: jsTreeData
            },

            plugins: ["types", "dnd", "state"]
        });


        tree.on({
        	// Auswahl-Listener
            "select_node.jstree": function (e, data) {
            	selectedNode = data.node.li_attr;

            },

            // Auswahl-Entfernen-Listener
            "deselect_node.jstree": function (e, data) {
            	selectedNode = null;
            },

	        // Doppelklick-Listener
            "dblclick.jstree": function (e, data) {
            	if (selectedNode['class'].indexOf('filesitem-file') >= 0) {
            		if (selectedNode["data-file-mime"] == "text/x-tex") {
            			// bei Doppelklick auf TEX-Datei zum Editor gehen
            			window.location.replace("/editor/#" + selectedNode["data-file-id"]);
            		}
            	}
            },

	        // Tasten-Listener
            "keydown": function (e, data) {
            },
        });
    }


    var fileTemplate = doT.template($("#template_filesitem-file").text()),
        folderTemplate = doT.template($("#template_filesitem-folder").text());

    function convertRawDataToJsTreeData(rawData) {
        var jsTreeData = [];
		
        $.each(rawData.folders || [], function (i, folder) {
            jsTreeData.push({
                id: "folder" + folder.id,
                text: folderTemplate(folder),
                icon: "glyphicon glyphicon-folder-open",
                li_attr: {"class": "filesitem-folder", "data-folder-id": folder.id, "folder-name": folder.name},
                children: convertRawDataToJsTreeData(folder)
            });
        });

        $.each(rawData.files || [], function (i, file) {
            file.createTime = getRelativeTime(file.createTime);
            file.lastModifiedTime = getRelativeTime(file.lastModifiedTime);
            file.size = Math.round(file.size / 1024); // in KB
			if(file.mimetype.indexOf("image") > -1){
				jsTreeData.push({
                id: "file" + file.id,
                text: fileTemplate(file),
                icon: "glyphicon glyphicon-file",
                li_attr: {"class": "filesitem-file", "data-file-id": file.id, "data-file-mime": file.mimetype}
            });
			}
 
        });

        return jsTreeData;
    }

    /*
     * Gibt das ID des ausgewähltes Verzeichnisses zurück (auch für ausgewählte Dateien)
     */
    function getSelectedFolderId() {
        var selectedNode = getSelectedNode();

        if (selectedNode['class'].indexOf('filesitem-folder') >= 0) {
            var selectedFolder = selectedNode;
        } else {
            selectedFolder = selectedNode.closest(".filesitem-folder");
        }

        return selectedFolder.data("folder-id") || rootFolderId;
    }


    function getSelectedNode() {
        return $("#" + tree.jstree().get_selected());
    }


    /*
     * Leitet den Benutzer zurück zur Projektverwaltung.
     */
    function backToProject() {
        // TODO: auf das richtige Projekt verweisen?
        window.location.replace("/projekt/");
    }


});
	
/**
* Einfügen des Dateipfades in die tex Datei
*/
var imageWidth;
function insertImageWithID(fileID, filePath){
	documentsJsonRequest({
			'command': 'fileinfo',
			'id': fileID,
		}, function(result, data) {
			if (result)
			{
				if(data.response.mimetype.indexOf("image") > -1){
					imageWidth = document.getElementById("imageWidth").value / 100;
					editor.insert("\\includegraphics[width="+imageWidth+"\\textwidth]{"+filePath+data.response.filename+"}"+"\n"); 
				};				
			}
	});

}

/**
* Aufruf durch dialog_grafik_einfuegen
* iteriert durch die im HTML Quellcode aufgebaute JSTree Struktur im 
* fileswrapper div element
*/
function insertGraphics(){
	
	var selectedArray = tree.jstree("get_selected");
	var substringID = null;
	var selectedFile;
	var filePath;
	var currElement;
	
	//für alle selektierten items
	for (var i = 0; i < selectedArray.length; i++) {
		filePath = "";
		selectedFile = selectedArray[i]; //eg. file10
		substringID = selectedFile.substr(4); //eg. 10
		if(isInt(substringID) == true){

			//suche im fileswrapper div nach allen li elementen
			$('#fileswrapper li').each(function(i)
			{
				//wenn die id des elements mit dem selektierten element übereinstimmt
			   if(selectedFile == $(this).attr('id')){
					//setze als aktuelles element, das hierarchisch in der DOM Struktur nächstgelegende ul element
					currElement = $(this).closest("ul");

					//iteriere durch die schleife solange bis das oberste ul element erreicht wurde
					//currElement.closest("li").attr('class') ist in dem fall nicht mehr definiert
					//da es über dem obersten ul element kein li element mehr gibt
					while(true){
					
						if (typeof currElement.closest("li").attr('class') !== 'undefined') {
							//prüfe ob aktuell übergeordnetes li element ein ordner ist
							//wenn ja füge den ordner namen zum dateipfad hinzu
							if(currElement.closest("li").attr('class').indexOf("filesitem-folder") > -1){
								currElement = currElement.closest("li");
								filePath = currElement.attr('folder-name')+ "/" + filePath;
								currElement = currElement.closest("ul");
							}
						} else{
							break;
						}

					}
					
					//wenn die schleife beendet wurde rufe die methode mit der file id auf und dem entsprechenden pfad
					insertImageWithID(substringID, filePath);
			   }
			});
		}
		
	}
	//deselektiere alle items und schließe den dialog
	tree.jstree("deselect_all");
	$( '#dialog_grafik_einfuegen' ).dialog('destroy');
}

/**
* prüfe ob eine variable vom typ integer ist
*/
function isInt(n) {
	return n % 1 === 0;
}
