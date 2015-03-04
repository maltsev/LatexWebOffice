var creatingFileNodeID = null;			// ID der Knoten-Komponente der derzeitig zu erstellenden Datei
var creatingFolderNodeID = null;		// ID der Knoten-Komponente des derzeitig zu erstellenden Verzeichnisses
var renamingNodeID = null;				// ID der/des derzeitig umzubenennenden Datei/Verzeichnisses
var prevName = null;					// Name der/des derzeitig umzubenennenden Datei/Verzeichnisses (für etwaiges Zurückbenennen)
var deletingNodeID = null;				// ID der/des derzeitig zu löschenden Datei/Verzeichnisses

var editMode = false;					// gibt an, ob sich eine der Knoten-Komponenten derzeitig im Editierungsmodus befindet

var selectedNodeID = "";				// ID der selektierten Knoten-Komponente
var prevSelectedNodeID 	= "";			// ID der selektierten Knoten-Komponente (wird nur durch neue Auswahl überschrieben) (notwendig bei Doppelklick)
var prevDnDParentFolderID = "";			// ID des vorherigen Überverzeichnisses einer vom Drag-and-Drop betroffenen Knoten-Komponente
										// (notwendig zur Unterscheidung, ob ein tatsächliches Verschieben erfolgt ist)
var postSelection = false;				// gibt an, ob eine explizite Nachselektion notwendig ist (bei 'Umbenennen')

var tree;
var treeInst;
var folderUntilRoot = 0;
var rootFolderId

var sorting = 0;						// Sortierungsvariable ( 0 = Name, 1 = Größe, 2 = Erstellungsdatum, 3 = Änderungsdatum, 4 = Typ )
var sortOrder = 1;						// Sortierungsrichtung ( 1 = aufsteigend, -1 = absteigend )
var ignoreSorting = false;				// für temporäres Ignorieren der Sortierung bei anlegender Knoten-Komponente ('Erstellen')
var sortReplacements = {"ä":"a", "ö":"o", "ü":"u", "ß":"ss" };

/*
@author: Timo Dümke, Ingolf Bracht, Kirill Maltsev
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 23.01.2015 - sprint-nr: 4
*/
$(function () {
	
    // ID zum vorliegenden Projekt
	rootFolderId = parseInt(location.hash.substr(1), 10);
	window.top.name = rootFolderId;
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
    
    // 'Sortieren nach Name'-Button
	$('.sort-0').click(function() {
		updateSorting(0);
	});
	// 'Sortieren nach Erstellungsdatum'-Button
	$('.sort-1').click(function() {
		updateSorting(1);
	});
	// 'Sortieren nach Autor'-Button
	$('.sort-2').click(function() {
		updateSorting(2);
	})
	// 'Sortieren nach Autor'-Button
	$('.sort-3').click(function() {
		updateSorting(3);
	})
	// 'Sortieren nach Autor'-Button
	$('.sort-4').click(function() {
		updateSorting(4);
	})
	
	initSorting();


	// ----------------------------------------------------------------------------------------------------
	//                                             MENÜ-EINTRÄGE                                           
	// ----------------------------------------------------------------------------------------------------
	
    // "Öffnen"-Schaltfläche
	$(".filestoolbar-open").click(function() {
		
		var selectedNodeObj = getSelectedNodeObject();
		
		// Datei
		if(selectedNodeObj.hasClass("filesitem-file")) {
			calculateFolderUntilRoot();
			window.location.assign("/editor/#" + selectedNodeObj.data("file-id"));
		}
		// Verzeichnis
		else if(selectedNodeObj.hasClass("filesitem-folder"))
			treeInst.toggle_node(selectedNodeID);
	});
	
	// "Datei Erstellen"-Schaltfläche
	$(".filestoolbar-newfile").click(function() {
		
		// Eltern-Knoten
		var par = '#';
		var selectedFolderID = getSelectedFolderId();
		if(treeInst.get_selected().length!=0 && !(getSelectedNodeObject().hasClass("filesitem-file") && selectedFolderID===rootFolderId))
			par = "folder"+selectedFolderID;
		
		// erzeugt eine neue Knoten-Komponente (als Datei) im ausgewählten Verzeichnis
		ignoreSorting = true;
		creatingFileNodeID = treeInst.create_node(par,{"type": "file"});
		treeInst.set_icon(creatingFileNodeID,"glyphicon glyphicon-file");
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
		ignoreSorting = true;
		creatingFolderNodeID = treeInst.create_node(par,{"type": "folder"});
		treeInst.set_icon(creatingFolderNodeID,"glyphicon glyphicon-folder-open");
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
		prevName = ""+treeInst.get_node(renamingNodeID).li_attr["data-name"];
		
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
	
	function calculateFolderUntilRoot(){
		
		var pathString = treeInst.get_path(prevSelectedNodeID,"~#####~");
		var splittedPathString = pathString.split("~#####~");
		
		folderUntilRoot = 0;
		for (var i = 0; i < splittedPathString.length; i++) {
			if(splittedPathString[i].indexOf("title=\"Verzeichnis\"") > -1){
				folderUntilRoot++;
			}
		}
		window.top.name = rootFolderId + "/" + folderUntilRoot;
		
	}
	
	// ----------------------------------------------------------------------------------------------------
	//                                                JSTREE                                               
	// ----------------------------------------------------------------------------------------------------
	
	function reloadProject() {
		
		documentsJsonRequest({
				'command': 'listfiles',
				'id': rootFolderId
			}, function(result, data) {
				if(!result) {
					showAlertDialog("Fehler",ERROR_MESSAGES.PROJECTNOTEXIST);
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
            ignoreSorting = false;
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
            plugins: ["dnd","sort","state","types"],
            sort: function(a,b) {
            	
            	if(ignoreSorting)
            		return -1;
            	
            	var compare = 0;
            	
            	var is_a_file = this.get_node(a).li_attr["data-file-id"],
            		is_b_file = this.get_node(b).li_attr["data-file-id"];
            	
            	// Verzeichnisse vor Dateien
            	if(is_a_file && !is_b_file)
            		return 1;
            	else if(!is_a_file && is_b_file)
            		return -1;
            	
            	// nur Dateien
            	if(is_a_file && is_b_file) {
            		
            		// Sortierung nach Größe (bei übereinstimmenden Größen zweier Dateien erfolgt Sortierung nach Name s.u.)
            		if(sorting==1 && this.get_node(a).li_attr["data-file-size"]!=this.get_node(b).li_attr["data-file-size"])
            			compare = this.get_node(a).li_attr["data-file-size"] > this.get_node(b).li_attr["data-file-size"] ? 1 : -1;
            		// Sortierung nach Erstellungsdatum
            		else if(sorting==2)
						compare = this.get_node(a).li_attr["data-file-createtime"] < this.get_node(b).li_attr["data-file-createtime"] ? 1 : -1;
					// Sortierung nach Änderungsdatum
					else if(sorting==3)
						compare = this.get_node(a).li_attr["data-file-lastmodifiedtime"] < this.get_node(b).li_attr["data-file-lastmodifiedtime"] ? 1 : -1;
					// Sortierung nach Typ (bei übereinstimmenden Typen zweier Dateien erfolgt Sortierung nach Name s.u.)
					else if(sorting==4 && (this.get_node(a).li_attr["data-file-mime"])!=(this.get_node(b).li_attr["data-file-mime"]))
						compare = (""+this.get_node(a).li_attr["data-file-mime"]) > (""+this.get_node(b).li_attr["data-file-mime"]) ? 1 : -1;
            		
            	}
            	
            	// wenn noch kein Vergleich (s.o.) erfolgt ist, ...
            	if(compare==0) {
            		// ... wird nach dem Namen sortiert
            		compare = (""+this.get_node(a).li_attr["data-name"]).toLowerCase().replace(/[äöüß]/g, function($0) { return sortReplacements[$0] }) >
            				  (""+this.get_node(b).li_attr["data-name"]).toLowerCase().replace(/[äöüß]/g, function($0) { return sortReplacements[$0] }) ? 1 : -1;
            	}
            	
            	return compare*sortOrder;
			}
        });

        treeInst = $(".fileswrapper").jstree(true);
        
		// ----------------------------------------------------------------------------------------------------
		//                                               LISTENER                                              
		// ----------------------------------------------------------------------------------------------------
		
		// Refresh-Listener (für Nachselektion, notwendig beim 'Umbenennen')
		tree.bind('refresh.jstree',function(e) {
			
			if(postSelection) {
				
				// stellt den Zustand des JSTrees (zusätzlich) wieder her
				// (es erfolgt keine zusätzliche Zustandsspeicherung)
				treeInst.restore_state();
				
				postSelection = false;
			}
			
		});
		
		// ----------------------------------------------------------------------------------------------------
		
		// Erzeugungs-Listener (für Auto-Selektion)
		tree.bind('create_node.jstree',function(e,data) {
			
			// selektiert die erzeugte KnencodeURIComponent(user)oten-Komponente
			selectNode(data.node);
			
		});
		
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
					calculateFolderUntilRoot();
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
				if(treeInst.get_text(creatingFileNodeID)=="") {
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
				if(treeInst.get_text(creatingFolderNodeID)=="") {
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
				
				// indiziert explizite Nachselektion (s. Refresh-Listener)
				postSelection = true;
				
				// ... und kein oder derselbe Name eingegeben wurde, ...
				if(treeInst.get_text(renamingNodeID)=="" || treeInst.get_text(renamingNodeID)===prevName) {
					// ... wird der Umbenennungs-Vorgang abgebrochen
					renamingID = null;
					reloadProject();
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
            "dnd_start.vakata": function (event, data) {
            	prevDnDParentFolderID = treeInst.get_node(data.data.nodes[0]).parent;
            }
        });
        $(document).on({
            "dnd_stop.vakata": function (event, data) {
            	
                var node = treeInst.get_node(data.data.nodes[0]),
                    nodeId = node.li_attr["data-file-id"] || node.li_attr["data-folder-id"],
                    command = node.type === "folder" ? "movedir" : "movefile",
                    folderId = parseInt(node.parent.replace("folder", ""), 10) || rootFolderId;
                           
                documentsJsonRequest({command: command, id: nodeId, folderid: folderId}, function(result, data) {
                    if(!result)
                        showAlertDialog((node.type==="folder" ? "Verzeichnis" : "Datei")+" verschieben",data.response);
					
					// wenn ein tatsächliches Verschieben (unterschiedliche Überverzeichnisse) erfolgte
					if(prevDnDParentFolderID!=node.parent)
						// aktualisiert die Anzeige der Dateistruktur
						reloadProject();
					
					prevDnDParentFolderID = "";
                });
            },
        });
    }
    
    
	// ----------------------------------------------------------------------------------------------------
    
    var fileTemplate = doT.template($("#template_filesitem-file").text()),
        folderTemplate = doT.template($("#template_filesitem-folder").text());
    
    function convertRawDataToJsTreeData(rawData) {
        var jsTreeData = [];
        
        $.each(rawData.folders || [], function (i, folder) {
        	
            jsTreeData.push({
                id: "folder" + folder.id,
                text: folderTemplate(folder),
                li_attr: {"class": "filesitem-folder", "data-folder-id": folder.id,
                									   "data-name": folder.name},
                children: convertRawDataToJsTreeData(folder)
            });
        });

        $.each(rawData.files || [], function (i, file) {
        	
        	var attrCreateTime = file.createTime,
        		attrLastModifiedTime = file.lastModifiedTime,
        		attrSize = file.size;
        	
            file.createTime = getRelativeTime(file.createTime);
            file.lastModifiedTime = getRelativeTime(file.lastModifiedTime);
            file.size = Math.round(file.size / 1024); // in KB
            
            jsTreeData.push({
                id: "file" + file.id,
                text: fileTemplate(file),
                li_attr: {"class": "filesitem-file", "data-file-id": file.id,
                									 "data-name": file.name,
                									 "data-file-createtime": attrCreateTime,
                									 "data-file-lastmodifiedtime": attrLastModifiedTime,
                									 "data-file-mime": file.mimetype,
                									 "data-file-size": attrSize}
            });
        });

        return jsTreeData;
    }
	
	
	
	// ----------------------------------------------------------------------------------------------------
	//                                           FUNKTIONALITÄTEN                                          
	//                                      (client- und serverseitig)                                     
	// ----------------------------------------------------------------------------------------------------
	
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
				
				// wenn eine entsprechendes Datei angelegt werden konnte
				if(result)
					treeInst.set_id(treeInst.get_node(creatingFileNodeID),"file"+data.response.id);
				else
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
				if(result)
					treeInst.set_id(treeInst.get_node(creatingFolderNodeID),"folder"+data.response.id);
				else
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
	
	/*
	 * Benennt die/das betroffene Datei/Verzeichnis nach dem angegebenen Namen um.
	 * 
	 * @param name neuer Name für die/das betroffene Datei/Verzeichnis
	 */
	function renameItem(name) {
		
		var selectedNodeObj	= $("#"+renamingNodeID),
			commandName		= selectedNodeObj.hasClass("filesitem-folder") ? "renamedir" : "renamefile",
			itemId			= selectedNodeObj.data("file-id") || selectedNodeObj.data("folder-id");
		
		if(selectedNodeObj.hasClass("filesitem-file") && name.indexOf(".")===-1) {
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
					
					//$("> .jstree-anchor .filesitem-name", selectedNodeObj).text(name);
					//selectedNodeObj.data("name",name);
					
	            	// setzt die Umbenennungs-IDs zurück
					renamingNodeID = null;
					prevName = null;
					
	            }
	            // wenn die/das ausgewählte Datei/Verzeichnis für den übergebenen Namen nicht umbenannt werden konnte, ...
				else
					showAlertDialog((selectedNodeObj.hasClass("filesitem-file") ? "Datei" : "Verzeichnis")+" umbenennen",data.response);
				
				// aktualisiert die Anzeige der Verzeichnisstruktur
				reloadProject();
			});
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
	
	// ----------------------------------------------------------------------------------------------------
	//                                      ALLGEMEINE HILFSFUNKTIONEN                                     
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
	 * Liefert den aktuellen Cookie-Schlüssel.
	 */
	function getCookieKey(sortValue) {
		return encodeURIComponent(user)+"#F";
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
	 * Initialisierung die Sortierungsvariablen und -icons gemäß der vorliegenden Cookies.
	 * Liegen keine entsprechenden Cookies vor, erfolgt eine Initialisierung gemäß der Initialwerte der Sortierungsvariablen (nach Name, aufsteigend).
	 */
	function initSorting() {
		
		var cookies = document.cookie.split('; ');
		for(var i=0; i<cookies.length; i++) {
			
			key   = cookies[i].substr(0,cookies[i].indexOf("="));
			value = cookies[i].substr(cookies[i].indexOf("=")+1);
			
			if(key==getCookieKey()) {
				values = value.split(',');
				if(values.length==2 && !isNaN(values[0]) && !isNaN(values[1])) {
					
					// Sortierungswert
					sortingNum = parseInt(values[0]);
					if(0<=sortingNum && sortingNum<=4)
						sorting = sortingNum;
					
					// Sortierungsrichtung
					sortOrderNum = parseInt(values[1]);
					if(sortOrderNum==1 || sortOrderNum==-1)
						sortOrder = sortOrderNum;
				}
			}
		}
		
		// initialisiert das Sortierungsicon im entsprechenden Menü-Eintrag
		if(sortOrder==1)
			$('.sort-'+sorting).children('.glyphicon').addClass('glyphicon-arrow-down');
		else {
			$('.sort-'+sorting).children('.glyphicon').removeClass('glyphicon-arrow-down');
			$('.sort-'+sorting).children('.glyphicon').addClass('glyphicon-arrow-up');
		}
		$('.sort-'+sorting).children('.glyphicon').removeAttr("data-hidden");
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
		$(".filestoolbar-open").prop("disabled", !texFile && file);
		$(".filestoolbar-newfile").prop("disabled", !basic);
		$(".filestoolbar-newfolder").prop("disabled", !basic);
		$(".filestoolbar-delete").prop("disabled", !selected);
		$(".filestoolbar-rename").prop("disabled", !selected);
		$(".filestoolbar-download").prop("disabled", !selected);
		$(".filestoolbar-upload").prop("disabled", file);
	}
	
	/*
	 * Aktualisiert die Sortierung gemäß des übergebenen Sortierungswertes.
	 *
	 * @param newSorting neuer Sortierungswert ( 0 = Name, 1 = Erstellungsdatum, 2 = Autor )
	 */
	function updateSorting(newSorting) {
		
		// derzeitiges Sortierungsicon
		var icon = 'glyphicon-arrow-down';
		if(sortOrder==-1)
			icon = 'glyphicon-arrow-up';
		
		// Icon der derzeitigen Sortierung wird entfernt bzw. versteckt
		if(sorting==newSorting)
			$('.sort-'+sorting).children('.glyphicon').removeClass(icon);
		else {
			if($('.sort-'+sorting).children('.glyphicon').hasClass('glyphicon-arrow-up'))
				$('.sort-'+sorting).children('.glyphicon').removeClass(icon).addClass('glyphicon-arrow-down');
			$('.sort-'+sorting).children('.glyphicon').attr("data-hidden","hidden");
		}	
		
		// neue Sortierungsrichtung
		if(sorting==newSorting)
			sortOrder *= -1;
		else
			sortOrder = 1;
		
		// neues Sortierungsicon
		icon = 'glyphicon-arrow-down';
		if(sortOrder==-1)
			icon = 'glyphicon-arrow-up';
		
		// fügt das Icon für die neue Sortierung hinzu
		$('.sort-'+newSorting).children('.glyphicon').addClass(icon);
		$('.sort-'+newSorting).children('.glyphicon').removeAttr("data-hidden");
		
		sorting = newSorting;
		
		// speichert die Sortierung für den derzeitigen Nutzer im entsprechenden Cookie
		document.cookie = getCookieKey()+"="+sorting+","+sortOrder+"; expires="+Number.POSITIVE_INFINITY+"; path=/";
		
		ignoreSorting = false;
		treeInst.refresh();
		
	}
});