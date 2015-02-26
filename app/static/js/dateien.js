var creatingFileNodeID = null;			// ID der Knoten-Komponente der derzeitig zu erstellenden Datei
var creatingFolderNodeID = null;		// ID der Knoten-Komponente des derzeitig zu erstellenden Verzeichnisses
var renamingNodeID = null;				// ID der/des derzeitig umzubenennenden Datei/Verzeichnisses
var prevName = null;					// Name der/des derzeitig umzubenennenden Datei/Verzeichnisses (für etwaiges Zurückbenennen)
var deletingNodeID = null;				// ID der/des derzeitig zu löschenden Datei/Verzeichnisses

var editMode = false;					// gibt an, ob sich eine der Knoten-Komponenten derzeitig im Editierungsmodus befindet

var selectedNodeID = "";				// ID der selektierten Knoten-Komponente
var prevSelectedNodeID 	= "";			// ID der selektierten Knoten-Komponente (wird nur durch neue Auswahl überschrieben) (notwendig bei Doppelklick)

var tree;
var treeInst;

/*
@author: Timo Dümke, Ingolf Bracht, Kirill Maltsev
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 23.01.2015 - sprint-nr: 4
*/
$(function () {
	
    // ID zum vorliegenden Projekt
	var rootFolderId = parseInt(location.hash.substr(1), 10);
	if (! rootFolderId) {
		window.location.replace("/projekt/");
	    return;
	}
	
	// Modal zum Bestätigen/Abbrechen des Löschvorgangs
	// 'Ja'-Button des Modals zur Bestätigung des Löschvorgangs
	$('.modal_deleteConfirmation_yes').on("click", function() {
		deleteItem();
	})
	
	
    reloadProject();


	// -------------------------------------------------------------------------
	//                              MENÜ-EINTRÄGE
	// -------------------------------------------------------------------------

    // "Öffnen"-Schaltfläche
	$(".filestoolbar-open").click(function() {
	    var selectedNode = getSelectedNodeObject();
		window.location.assign("/editor/#" + selectedNode.data("file-id"));
	});

	// "Datei Erstellen"-Schaltfläche
	$(".filestoolbar-newfile").click(function() {
		
		// Eltern-Knoten
		var par = '#';
		var selectedFolderID = getSelectedFolderId();
		if(treeInst.get_selected().length!=0 && !(getSelectedNodeObject().hasClass("filesitem-file") && selectedFolderID===rootFolderId))
			par = "folder"+selectedFolderID;
		
		// erzeugt eine neue Knoten-Komponente (als Datei) im ausgewählten Verzeichnis
		creatingFileNodeID = treeInst.create_node(par,{"type": "file"});
		// selektiert die erzeugte Knoten-Komponente
		selectNode(creatingFileNodeID);
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		editNode(creatingFileNodeID,"");
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen (vollständige Deaktivierung)
		updateMenuButtons();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird createFile() zum serverseitigen Erstellen eines entsprechenden Projektes aufgerufen
	
	});
	
	// "Verzeichnis Erstellen"-Schaltfläche
	$(".filestoolbar-newfolder").click(function() {
		
		// Eltern-Knoten
		var par = '#';
		var selectedFolderID = getSelectedFolderId();
		if(treeInst.get_selected().length!=0 && !(getSelectedNodeObject().hasClass("filesitem-file") && selectedFolderID===rootFolderId))
			par = "folder"+selectedFolderID;
		
		// erzeugt eine neue Knoten-Komponente (als Verzeichnis) im ausgewählten Verzeichnis
		creatingFolderNodeID = treeInst.create_node(par,{"type": "folder"});
		// selektiert die erzeugte Knoten-Komponente
		selectNode(creatingFolderNodeID);
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		editNode(creatingFolderNodeID,"");
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen (vollständige Deaktivierung)
		updateMenuButtons();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird createFolder() zum serverseitigen Erstellen eines entsprechenden Projektes aufgerufen
		
	});
	
	// "Löschen"-Schaltfläche
	$(".filestoolbar-delete").click(function() {
		
		deletingNodeID = selectedNodeID;
		
		deleteSelectedNode();
		
	});
	
	// "Umbenennen"-Schaltfläche
	$(".filestoolbar-rename").click(function() {
		
		var node = treeInst.get_node(selectedNodeID);
		// ID der/des umzubenennenden Datei/Verzeichnisses
		renamingNodeID = node.id;
		// derzeitiger Name der/des Datei/Verzeichnisses (für etwaiges Zurückbenennen)
		prevName = $("#"+renamingNodeID).data("name");
		
		// versetzt die Knoten-Komponente in den Bearbeitungsmodus
		editNode(renamingNodeID,prevName);
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtons();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird renameItem() zum serverseitigen Umbenennen der/des betroffenen Datei/Verzeichnisses aufgerufen
	});
	
	// "Herunterladen"-Schaltfläche
	$(".filestoolbar-download").click(function() {
		
	    var selectedNode = getSelectedNodeObject();
	    
		if(selectedNode.hasClass("filesitem-file")) {
			documentsRedirect({
				'command': 'downloadfile',
				'id': selectedNode.data("file-id")
			});
		}
		else if(selectedNode.hasClass("filesitem-folder")) {
			documentsRedirect({
				'command': 'exportzip',
				'id': selectedNode.data("folder-id")
			});
		}
	});
	
	// "Hochladen"-Schaltfläche
	$(".filestoolbar-upload").click(function() {
		
		dialogUploadFile();
		
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	function reloadProject() {
		
		documentsJsonRequest({
				'command': 'listfiles',
				'id': rootFolderId
			}, function(result, data) {
				if(!result) {
					alert(ERROR_MESSAGES.PROJECTNOTEXIST);
					return;
				}
				
				renderProject(data.response);
				updateMenuButtons();
        });
    }
	
    // folder: {icon: "glyphicon glyphicon-folder-open"},
    // emptyFolder: {icon: "glyphicon glyphicon-folder-close"},
    // file: {icon: "glyphicon glyphicon-file"},
    // pdf: {icon: "glyphicon glyphicon-book"}

    var tree = null;
    function renderProject(data) {
        var jsTreeData = convertRawDataToJsTreeData(data);

        if (tree) {
            treeInst.settings.core.data = jsTreeData;
            treeInst.refresh();
            return;
        }

        tree = $(".fileswrapper").jstree({
            core: {
                check_callback: true,
                multiple: false,
                data: jsTreeData
            },

            dnd: {
                "inside_pos": "last"
            },

            types: {
                "default":{
                    "icon" : "glyphicon glyphicon-file",
                    "valid_children": []
                },
                "file":{
                    "icon" : "glyphicon glyphicon-file",
                    "valid_children": []
                },
                "folder":{
                    "icon" : "glyphicon glyphicon-folder-open",
                    "valid_children": ["file", "default", "folder"]
                }
            },

            plugins: ["types", "dnd", "state"]
        });

        treeInst = $(".fileswrapper").jstree(true);
        
		// ----------------------------------------------------------------------------------------------------
		//                                               LISTENER                                              
		// ----------------------------------------------------------------------------------------------------
		
		// Auswahl-Listener
		tree.bind('select_node.jstree',function(e,data) {
			
			// Deselektion (die der Selection-ID zugehörige Knoten-Komponente wurde erneut selektiert)
			if(selectedNodeID===data.node.id) {
				
				// deselektiert die betroffene Knoten-Komponente
				treeInst.deselect_node(data.node);
				// setzt die Selection-ID zurück
				selectedNodeID = "";
				
			}
			// Selektion (eine Knoten-Komponente werde selektiert, deren ID nicht mit der Selection-ID übereinstimmt)
			else {
				
				// aktualisiert die Selection-ID gemäß der ausgewählten Knoten-Komponente
				selectedNodeID = data.node.id;
				prevSelectedNodeID = data.node.id;
				
			}
			
			// aktualisiert die Aktivierungen der Menü-Schaltflächen
			updateMenuButtons();
		});
		
		// ----------------------------------------------------------------------------------------------------
		
		// Doppelklick-Listener
		tree.bind("dblclick.jstree",function(e) {
			
			var selectedNode = $("#"+prevSelectedNodeID);
			if(selectedNode.hasClass("filesitem-file")) {
				if($.inArray(selectedNode.data("file-mime"), ["text/x-tex", "text/plain"])!=-1) {
					// bei Doppelklick auf TEX-Datei zum Editor gehen
					window.location.assign("/editor/#" + selectedNode.data("file-id"));
				}
			}
			
		});
		
		// ----------------------------------------------------------------------------------------------------
	
		// Tasten-Listener
		tree.bind('keydown',function(e) {
			
			// Entf-Taste
			if(e.keyCode===46 && !editMode) {
				
				deletingNodeID = selectedNodeID;
				
				deleteSelectedNode();
			}
		});
		
		// ----------------------------------------------------------------------------------------------------
	
		// Umbenennungs-Listener (für 'Erstellen' und 'Umbenennen')
		tree.bind('rename_node.jstree',function(e) {
			
			// blendet das Eingabe-Popover aus
			$('.input_popover').popover('hide');
			
			editMode = false;
			
			// wenn die Eingabe des Namens einer neuen Datei bestätigt wurde (= Datei erstellen), ...
			if(creatingFileNodeID!=null) {
				
				// ... und kein Name eingegeben wurde, ...
				if(treeInst.get_text(creatingFileNodeID)==="") {
					// ... wird der Erstellungs-Vorgang abgebrochen
					treeInst.delete_node(creatingFileNodeID);
					creatingFileNodeID = null;
					updateMenuButtons();
				}
				// ... und ein Name eingegeben wurde, ...
				else
					// ... wird severseitig ein neues Projekt mit dem festgelegten Namen erzeugt
					createFile(treeInst.get_text(creatingFileNodeID));
			}
			// wenn die Eingabe des Namens eines neuen Verzeichnisses bestätigt wurde (= Verzeichnis erstellen), ...
			if(creatingFolderNodeID!=null) {
				
				// ... und kein Name eingegeben wurde, ...
				if(treeInst.get_text(creatingFolderNodeID)==="") {
					// ... wird der Erstellungs-Vorgang abgebrochen
					treeInst.delete_node(creatingFolderNodeID);
					creatingFolderNodeID = null;
					updateMenuButtons();
				}
				// ... und ein Name eingegeben wurde, ...
				else
					// ... wird severseitig ein neues Verzeichnis mit dem festgelegten Namen erzeugt
					createFolder(treeInst.get_text(creatingFolderNodeID));
			}
			// wenn der neue Name für ein(e) bestehende(s) Datei/Verzeichnis bestätigt wurde (= Umbenennen)
			else if(renamingNodeID!=null) {
				
				// ... und kein oder derselbe Name eingegeben wurde, ...
				if(treeInst.get_text(renamingNodeID)==="" || treeInst.get_text(renamingNodeID)===prevName) {
					// ... wird der Umbenennungs-Vorgang abgebrochen
					node = treeInst.get_node(renamingNodeID);
					//treeInst.set_text(node,getHTML(node));
					renamingID = null;
					updateMenuButtons();
				}
				// ... und ein, vom bisherigen Namen verschiedener, Name eingegeben wurde, ...
				else
					// ... wird das serverseitige Umbenennen der/des betroffenen Datei/Verzeichnisses eingeleitet
					renameItem(treeInst.get_text(renamingNodeID));
		}
		});
		
		// ----------------------------------------------------------------------------------------------------
		
        tree.on({
            "ready.jstree refresh.jstree before_open.jstree": function () {
                $(".jstree-node").each(function () {
                    var node = $(this),
                        type = node.hasClass("filesitem-folder") ? "folder" : "file";

                    treeInst.set_type(node, type);
                });
            }
        });
		
		// ----------------------------------------------------------------------------------------------------
		
        $(document).on({
            "dnd_stop.vakata": function (event, data) {
                var node = treeInst.get_node(data.data.nodes[0]),
                    nodeId = node.li_attr["data-file-id"] || node.li_attr["data-folder-id"],
                    command = node.type === "folder" ? "movedir" : "movefile",
                    folderId = parseInt(node.parent.replace("folder", ""), 10) || rootFolderId;

                documentsJsonRequest({command: command, id: nodeId, folderid: folderId}, function(result, data) {
                    if(!result) {
                        showAlertDialog((node.type==="folder" ? "Verzeichnis" : "Datei")+" verschieben",data.response);
                        reloadProject();
                        return;
                    }
                });
            },
        });
    }

    /**
     * Öffnet den ausgewählten Knoten im Editor.
     */
    function openSelectedNode() {
    	var node = getSelectedNode();

    	// ist ein Knoten ausgewählt?
    	if (node.length) {
    		// Text- oder TEX-Datei?
    		if ($.inArray(node.data("file-mime"), ["text/x-tex", "text/plain"]) !== -1)
    		window.location.assign("/editor/#" + node.data("file-id"));
    	}
    }
    
    /**
     * Zeigt einen Dialog zum Löschen des ausgewählten Knotens an.
     */
    function deleteSelectedNode() {
    	
    	var node = getSelectedNodeObject();

    	// ist ein Knoten ausgewählt?
    	if (node.length) {
    		var isFile = node.hasClass("filesitem-file");
    		$('.filesdialog-delete-title').text('Löschen ' + (isFile ? 'der Datei' : 'des Verzeichnisses')
    				+ ' bestätigen');
    		$('.filesdialog-delete-text').text('Sind Sie sicher, dass Sie ' + (isFile ? 
    				'die ausgewählte Datei' : 'das ausgewählte Verzeichnis') + ' löschen wollen?');

    		$('.filesdialog-delete-yes').unbind();
    		$('.filesdialog-delete-yes').click(node, function(event) {
    			deleteItem();
    		});

    		$('.filesdialog-delete-no').unbind();
    		$('.filesdialog-delete-no').click(function() {
    			tree.focus();
    		});

    		$('.filesdialog-delete').modal('show');
    	}
    }
    
    /**
     * Zeigt einen Dialog zum Hochladen einer Datei an.
     */
    function dialogUploadFile() {
    	
    	var node = getSelectedNodeObject();

    	$('.filesdialog-upload-message').addClass('invisible');

    	$('.filesdialog-upload-files').val('');
    	$('.filesdialog-upload-files').unbind();
    	$('.filesdialog-upload-files').change(function() {
    		$('.filesdialog-upload-do').prop('disabled', 
    				$('.filesdialog-upload-files').val() == '');
    	});

    	$('.filesdialog-upload-folderid').val(node.length ?
    			getSelectedFolderId() : rootFolderId);

    	$('.filesdialog-upload-do').prop('disabled', true);
    	$('.filesdialog-upload-do').unbind();
		$('.filesdialog-upload-do').click(function() {
			$('.filesdialog-upload-form').submit();
		});

		$('.filesdialog-upload-abort').unbind();
		$('.filesdialog-upload-abort').click(function() {
			tree.focus();
		});

		$('.filesdialog-upload-form').unbind();
    	$('.filesdialog-upload-form').submit(function(event) {
    		// Formular deaktivieren
    		event.preventDefault();
    		$('.filesdialog-upload-do').prop('disabled', true);

    		// Dateien senden
    		var form = new FormData(this);
    		documentsJsonRequest(form, function(result, data) {
    			reloadProject();
    			if (result && data.response.failure.length == 0) {
    				$('.filesdialog-upload').modal('hide');
    				tree.focus();
    			} else {
    				var msg = $('.filesdialog-upload-message');
    				msg.text('Fehler beim Hochladen!');
    				if (data.response.failure)
	    				for (var i = 0; i < data.response.failure.length; ++i)
	    					msg.append($('<br />'))
	    							.append($('<b></b>').text(data.response.failure[i].name))
	    							.append(document.createTextNode(': ' + 
	    								data.response.failure[i].reason));
    				else
    					msg.append($('<br />'))
								.append(document.createTextNode(data.response));
    				msg.removeClass('invisible');

    				$('.filesdialog-upload-files').val('');
    				$('.filesdialog-upload-do').prop('disabled', false);
    			}
    		}, false, false);
    	});

    	$('.filesdialog-upload').modal('show');
    }


    var fileTemplate = doT.template($("#template_filesitem-file").text()),
        folderTemplate = doT.template($("#template_filesitem-folder").text());

    function convertRawDataToJsTreeData(rawData) {
        var jsTreeData = [];

        $.each(rawData.folders || [], function (i, folder) {
            jsTreeData.push({
                id: "folder" + folder.id,
                text: folderTemplate(folder),
                li_attr: {"class": "filesitem-folder", "data-folder-id": folder.id, "data-name": folder.name},
                children: convertRawDataToJsTreeData(folder)
            });
        });

        $.each(rawData.files || [], function (i, file) {
            file.createTime = getRelativeTime(file.createTime);
            file.lastModifiedTime = getRelativeTime(file.lastModifiedTime);
            file.size = Math.round(file.size / 1024); // in KB

            jsTreeData.push({
                id: "file" + file.id,
                text: fileTemplate(file),
                li_attr: {"class": "filesitem-file", "data-file-id": file.id, "data-name": file.name, "data-file-mime": file.mimetype}
            });
        });

        return jsTreeData;
    }



/*
 * Erstellt eine neue tex-Datei mit dem übergebenen Namen im zuvor ausgewählten Verzeichnis.
 *
 * @param name Name für die zu erstellende Datei
 */
function createFile(name) {
	
	// vermeiden "filename.tex.tex" Namen
	name = name.replace(/\.tex/i, "") + ".tex";
	
	var selectedFolderId = getSelectedFolderId();
	
	// erzeugt severseitig eine neue tex-Datei mit dem festgelegten Namen im aktuellen Verzeichnis
	documentsJsonRequest({
			'command': 'createtex',
			'id': selectedFolderId,
			'name': name
		}, function(result,data) {
			// wenn eine entsprechendes Datei nicht angelegt werden konnte
			if(!result)
				showAlertDialog("Datei erstellen",data.response);
			
			// setzt die Erstellungs-ID zurück
			creatingFileNodeID = null;
			
			// aktualisiert die Anzeige der Dateistruktur
			reloadProject();
	});
}

/*
 * Erstellt ein neues Verzeichnis mit dem übergebenen Namen im zuvor ausgewählten Verzeichnis.
 *
 * @param name Name für das zu erstellende Verzeichnis
 */
function createFolder(name) {
	
	var selectedFolderId = getSelectedFolderId();
	
	// erzeugt severseitig ein neues Verzeichnis mit dem festgelegten Namen im aktuellen Verzeichnis
	documentsJsonRequest({
			'command': 'createdir',
			'id': selectedFolderId,
			'name': name
		}, function(result,data) {
			// wenn ein entsprechendes Verzeichnis nicht angelegt werden konnte
			if(!result)
				showAlertDialog("Verzeichnis erstellen",data.response);
			
			// setzt die Erstellungs-ID zurück
			creatingFolderNodeID = null;
			
			// aktualisiert die Anzeige der Verzeichnisstruktur
			reloadProject();
	});
}

/*
 * Löscht die/das momentan ausgewählte Datei/Verzeichnis.
 */
function deleteItem() {
	
	var selectedNode = $("#"+deletingNodeID);
	
	if(selectedNode.hasClass("filesitem-file")) {
		documentsJsonRequest({
				'command': 'deletefile',
				'id': selectedNode.data("file-id")
			}, function(result,data) {
				if(result) {
					
					// entfernt die zugehörige Knoten-Komponente
					treeInst.delete_node(deletingNodeID);
					
					// setzt die Löschung-ID zurück
					deletingNodeID = null;
					// setzt die Selektions-ID zurück
					selectedNodeID = "";
				}
				else
					showAlertDialog("Datei löschen",data.response);
				
				// aktualisiert die Anzeige der Verzeichnisstruktur
				reloadProject();
		});
	}
	else if(selectedNode.hasClass("filesitem-folder")) {
		documentsJsonRequest({
				'command': 'rmdir',
				'id': selectedNode.data("folder-id")
			}, function(result,data) {
				if(result) {
					
					// entfernt die zugehörige Knoten-Komponente
					treeInst.delete_node(deletingNodeID);
					
					// setzt die Löschung-ID zurück
					deletingNodeID = null;
					// setzt die Selektions-ID zurück
					selectedNodeID = "";
					
				}
				else
					showAlertDialog("Verzeichnis löschen",data.response);
				
				// aktualisiert die Anzeige der Verzeichnisstruktur
				reloadProject();
		});
	}
}

/*
 * Benennt die/das betroffene Datei/Verzeichnis nach dem angegebenen Namen um.
 * 
 * @param name neuer Name für die/das betroffene Datei/Verzeichnis
 */
function renameItem(name) {
	
	var selectedNode	= $("#"+renamingNodeID),
		commandName		= selectedNode.hasClass("filesitem-folder") ? "renamedir" : "renamefile",
		itemId			= selectedNode.data("file-id") || selectedNode.data("folder-id");
	
	if(selectedNode.hasClass("filesitem-file") && name.indexOf(".")===-1) {
		showAlertDialog("Datei umbenennen","Bitte geben Sie auch die Datei-Namenserweiterung ein.");
		reloadProject();
		return;
	}
	
	documentsJsonRequest({
			'command': commandName,
			'id': itemId,
			'name': name
		}, function(result, data) {
			// wenn die/das ausgewählte Datei/Verzeichnis erfolgreich umbenannt wurde, ist der Umbenennungs-Vorgang abgeschlossen
            if(result) {
            	
            	// setzt die Umbenennungs-IDs zurück
				renamingID = null;
				prevName = null;
				
				$("> .jstree-anchor .filesitem-name", selectedNode).text(name);
            }
            // wenn die/das ausgewählte Datei/Verzeichnis für den übergebenen Namen nicht umbenannt werden konnte, ...
			else
				showAlertDialog((selectedNode.hasClass("filesitem-file") ? "Datei" : "Verzeichnis")+" umbenennen",data.response);
			
			// aktualisiert die Anzeige der Verzeichnisstruktur
			reloadProject();
		});
}


// ----------------------------------------------------------------------------------------------------

/*
 * Versetzt die, der übergebenen ID entsprechende, Knoten-Komponente in den Bearbeitungsmodus.
 *
 * @param nodeID ID der Knoten-Komponente, deren Name bearbeitet werden soll
 * @param text Text-Vorgabe zur Editierung
 */
function editNode(nodeID,text) {
	
	editMode = true;
	
	// zeigt das Eingabe-Popover in relativer Position zur betroffenen Knoten-Komponente an
	showPopover(treeInst.get_node(nodeID));
	// versetzt die betroffene Knoten-Komponente in den Bearbeitungsmodus
	treeInst.edit(nodeID,text);
}

/*
 * Liefert die ID des aktuellen Verzeichnisses.
 *
 * @return die ID des aktuell selektierten Verzeichnisses, sofern ein Verzeichnis selektiert ist oder
 *         die ID des direkten Überverzeichnisses der aktuell selektierten Datei, sofern eine Datei selektiert ist oder
 *         die ID des root-Verzeichnisses, sofern weder ein Verzeichnis, noch eine Datei selektiert sind
 */
function getSelectedFolderId() {
	
	var selectedNodeObj = getSelectedNodeObject();
	
	if(selectedNodeObj.hasClass("filesitem-folder"))
		var selectedFolder = selectedNodeObj;
	else
		selectedFolder = selectedNodeObj.closest(".filesitem-folder");
	
	return selectedFolder.data("folder-id") || rootFolderId;
}

/*
 * Liefert das Objekt der momentan ausgewählten Knoten-Komponente.
 *
 * @return das Objekt der momentan ausgewählten Knoten-Komponente
 */
function getSelectedNodeObject() {
	
	return $("#"+treeInst.get_selected());
	
}

/*
 * Selektiert die, der übergebenen ID entsprechende, Knoten-Komponente.
 * Hierbei wird die momentan ausgewählte Knoten-Komponente deselektiert.
 *
 * @param nodeID ID der Knoten-Komponente, welche selektiert werden soll
 */
function selectNode(nodeID) {
	
	treeInst.deselect_node(treeInst.get_selected());
	treeInst.select_node(nodeID);
	selectedNodeID = nodeID;
}

/*
 * Zeigt das Popover in relativer Position zur übergebenen Knoten-Komponente an.
 *
 * @param node Knoten-Komponente zu deren Position das Popover relativ angezeigt werden soll
 */
function showPopover(node) {
	
	if(node!=null && treeInst.get_node(node.id)) {
		
		var popover = $('.input_popover');
		
		// zeigt das Popover an und richtet es links über der Knoten-Komponente aus
		// (Reihenfolge nicht verändern!)
		popover.popover('show');
        $('.popover').css('left',$("#"+node.id).position().left+'px');
        $('.popover').css('top',($("#"+node.id).position().top-43)+'px');
	}
}

/*
 * Aktualisiert die Aktivierungen der Menü-Schaltflächen.
 */
function updateMenuButtons() {
	
	// flags für die Aktivierung der Schaltflächen
	var basic = true;
	
	// Editierungsmodus
	if(editMode) {
		// keine Aktivierungen
		basic 		= false;
		selected 	= false;
		folder 		= false;
		file 		= true;
		texFile 	= false;
	}
	else {
		var selectedNodeObj = getSelectedNodeObject();
		
		// flag für die Aktivierung der selektionsabhängigen Schaltflächen
		selected = selectedNodeObj.length;
		folder = selected && selectedNodeObj.hasClass("filesitem-folder");
		file = selected && selectedNodeObj.hasClass("filesitem-file");
		texFile = file && $.inArray(selectedNodeObj.data("file-mime"), ["text/x-tex", "text/plain"]) !== -1;
	}
	
	// setzt die Aktivierungen der einzelnen Menü-Schaltflächen
	$(".filestoolbar-open").prop("disabled", !texFile);
	$(".filestoolbar-newfile").prop("disabled", !basic);
	$(".filestoolbar-newfolder").prop("disabled", !basic);
	$(".filestoolbar-delete").prop("disabled", !selected);
	$(".filestoolbar-rename").prop("disabled", !selected);
	$(".filestoolbar-download").prop("disabled", !selected);
	$(".filestoolbar-upload").prop("disabled", file);
}
});