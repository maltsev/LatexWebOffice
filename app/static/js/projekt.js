/*
 * @author: Thore Thießen, Ingolf Bracht, Munzir Mohamed
 * @creation: 04.12.2014 - sprint-nr: 2
 * @last-change: 15.01.2015 - sprint-nr: 4
 */

// ID der Knoten-Komponente des derzeitig zu erstellenden Projektes
var creatingNodeID = null;
// ID des derzeitig umzubenennenden Projektes
var renameID = null;
// Name des derzeitig umzubenennenden Projektes (für etwaiges Zurückbenennen)
var prevName = null;
// ID der Knoten-Komponente des derzeitig zu duplizierenden Projektes
var duplicateNodeID = null;
// ID des derzeitig zu duplizierenden Projektes
var duplicateID = null;

var selectedNodeID = "";
var prevSelectedNodeID 	= "";

/*
 * Referenziert eine bestehende JSTree-Instanz (ohne eine neue zu erzeugen)
 * (zu verwenden, um darauf knotenspezifische Methoden anzuwenden)
 */
var treeInst;

/*
 * Initialisiert den JSTree und die Menü-Einträge.
 */
$(document).ready(function() {
	
	/*
	 * Erzeugt eine neue JSTree-Instanz
	 * (zu verwenden, um darauf instanz-spezifische Methoden (z.B. für Listener) anzuwenden)
	 *
	 * Plugins:	'state' zum browser-seitigen Speichern der geöffneten und ausgewählten Knoten-Komponenten
	 * 					(notwendig, da beim Aktualisieren der Seite die Auswahl verloren geht, die Menü-Einträge jedoch ggf. aktiviert bleiben)
	 */
	var tree = $('.projectswrapper').jstree({"core"    : {"check_callback" : true,"multiple" : false},
											 "plugins" : ["state"]});
	
	/*
	 * Referenziert eine bestehende JSTree-Instanz (ohne eine neue zu erzeugen)
	 * (zu verwenden, um darauf knotenspezifische Methoden anzuwenden)
	 */
	treeInst = $('.projectswrapper').jstree();
	
	
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
		
		// TEST METADATA
		//node = treeInst.get_node(selectedNodeID);
		//console.log("AUTHOR: "+node.author+" ..... CREATETIME: "+node.createtime+" ..... ROOTID: "+node.rootid);
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtons();
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Doppelklick-Listener
	tree.bind("dblclick.jstree",function(e) {
		
		openProject();
		
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Tasten-Listener
	tree.bind('keydown',function(e) {
		
		// TEMP
		//console.log(e.keyCode);
		
		switch(e.keyCode) {
			
			// Enter-Taste (Öffnen)
			case 13:
				
				// TODO (serverseitiges Öffnen)
				
				break;
			
			// Entf-Taste (Löschen)
			case 46:
				
				deleteProject();
				
				break;
		}
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Umbenennungs-Listener (für 'Erstellen' und 'Umbenennen')
	tree.bind('rename_node.jstree',function(e) {
		
		// wenn die Eingabe des Namens eines neuen Projektes bestätigt wurde (= Erstellen eines Projektes), ...
		if(creatingNodeID!=null) {
			
			// ... und kein Name eingegeben wurde, ...
			if(treeInst.get_text(creatingNodeID)==="") {
				// ... wird der Erstellungs-Vorgang abgebrochen
				treeInst.delete_node(creatingNodeID);
				creatingNodeID = null;
				updateMenuButtons();
			}
			// ... und ein Name eingegeben wurde, ...
			else
				// ... wird severseitig ein neues Projekt mit dem festgelegten Namen erzeugt
				createProject(treeInst.get_text(creatingNodeID));
		}
		// wenn die EIngabe des Names eines zu duplizierenden Projektes bestätigt wurde (= Duplizieren eines Projektes), ...
		else if(duplicateID!=null) {
		
			// ... und kein Name eingegeben wurde, ...
			if(treeInst.get_text(duplicateNodeID)==="") {
				// ... wird der Duplizierungs-Vorgang abgebrochen
				treeInst.delete_node(duplicateNodeID);
				duplicateNodeID = null;
				duplicateID = null;
				updateMenuButtons();
			}
			// ... und ein Name eingegeben wurde, ...
			else
				// ... wird serverseitig das zum duplizieren ausgewählte Projekt mit dem festgelegten Namen dupliziert
				duplicateProject(duplicateID,treeInst.get_text(duplicateNodeID));
		}
		// wenn der neue Name für ein bestehendes Projekt bestätigt wurde (= Umbenennen)
		else if(renameID!=null) {
			
			// ... und kein Name eingegeben wurde, ...
			if(treeInst.get_text(renameID)==="") {
				// ... wird der Umbenennungs-Vorgang abgebrochen
				treeInst.set_text(renameID,prevName);
				renameID = null;
				updateMenuButtons();
			}
			// ... und ein Name eingegeben wurde, ...
			else
				// ... wird das serverseitige Umbenennen des betroffenen Projektes eingeleitet
				renameProject(treeInst.get_text(renameID));
		}
		
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	initProjects();	
	
	// ----------------------------------------------------------------------------------------------------
	//                                             MENÜ-EINTRÄGE                                           
	// ----------------------------------------------------------------------------------------------------
	
	// 'Öffnen'-Schaltfläche
	$('.projecttoolbar-open').on("click", function() {
		
		openProject();
		
	});
	
	// 'Erstellen'-Schaltfläche
	$('.projecttoolbar-new').on("click", function() {
		
		// erzeugt eine neue Knoten-Komponente
		creatingNodeID = treeInst.create_node("#","");
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		treeInst.edit(creatingNodeID,"");
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen (vollständige Deaktivierung)
		updateMenuButtons();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird createProject() zum serverseitigen Erstellen eines entsprechenden Projektes aufgerufen
	});
	
	// 'Löschen'-Schaltfläche
	$('.projecttoolbar-delete').on("click", function() {
		
		deleteProject();
		
	});
	
	// 'Umbenennen'-Schaltfläche
	$('.projecttoolbar-rename').on("click", function() {
		
		// Projekt-ID des umzubenennenden Projektes
		renameID = selectedNodeID;
		// derzeitiger Name des Projektes (für etwaiges Zurückbenennen)
		prevName = treeInst.get_text(treeInst.get_node(renameID));
		
		// versetzt die zugehörige Knoten-Komponente in den Bearbeitungsmodus
		treeInst.edit(renameID);
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtons();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird renameProject() zum serverseitigen Umbenennen des betroffenen Projektes aufgerufen
		
	});
	
	// 'Duplizieren'-Schaltfläche
	$('.projecttoolbar-duplicate').on("click", function() {
		
		// Projekt-ID des zu duplizierenden Projektes
		duplicateID = selectedNodeID;
		
		// erzeugt eine neue Knoten-Komponente
		duplicateNodeID = treeInst.create_node("#","");
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		treeInst.edit(duplicateNodeID,"");
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen (vollständige Deaktivierung)
		updateMenuButtons();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird duplicateProject() zum serverseitigen Duplizieren eines entsprechenden Projektes aufgerufen		
		
	});
	
	// 'in Vorlage umwandeln'-Schaltfläche
	$('.projecttoolbar-converttotemplate').on("click", function() {
		
		// TODO
		
	});
	
	// 'Export'-Schaltfläche
	$('.projecttoolbar-export').on("click", function() {

		exportZip();
		
	});
	
	// 'Import'-Schaltfläche
	$('.projecttoolbar-import').on("click", function() {
		
		importZip();
		// TODO
		
	});
});

// ----------------------------------------------------------------------------------------------------
//                                           FUNKTIONALITÄTEN                                          
//                                      (client- und serverseitig)                                     
// ----------------------------------------------------------------------------------------------------

/*
 * Öffnet das momentan ausgewählte Projekt durch Wechseln zu dessen Datei-Übersicht.
 */
function openProject() {
	
	document.location.assign('/dateien/#' + treeInst.get_node(prevSelectedNodeID).rootid);
	
}

/*
 * Erstellt ein neues Projekt mit dem übergebenen Namen.
 *
 * @param name Name für das zu erstellende Projekt
 */
function createProject(name) {
	
	// erzeugt severseitig ein neues Projekt mit dem festgelegten Namen
	documentsJsonRequest({
			'command': 'projectcreate',
			'name': name
		}, function(result,data) {
			// wenn ein entsprechendes Projekt erstellt wurde, ist der Erstellungs-Vorgang abgeschlossen
			if(result) {
				
				// übernimmt die Daten des erzeugten Projektes in die angelegte Knoten-Komponente
				fillNode(creatingNodeID,data.response);
				
				// setzt die Erstellungs-ID zurück
				creatingNodeID = null;
				
				// aktualisiert die Aktivierungen der Menü-Schaltflächen (temporäre vollständige Deaktivierung wird aufgehoben)
				updateMenuButtons();
			}
			// wenn ein entsprechendes Projekt nicht angelegt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				treeInst.edit(creatingNodeID,"");
				
				// TEMP
				alert(data.response);
			}
	});
	
	
}

/*
 * Löscht das momentan ausgewählte Projekt.
 */
function deleteProject() {
	
	documentsJsonRequest({
			'command': 'projectrm',
			'id': treeInst.get_selected()[0]
		}, function(result,data) {
			// wenn das ausgewählte Projekt erfolgreich gelöscht wurde, ...
			if(result) {
				
				// ... wird die zugehörige Knoten-Komponente entfernt
				treeInst.delete_node(treeInst.get_selected()[0]);
				selectedNodeID = "";
				
				// aktualisiert die Aktivierungen der Menü-Schaltflächen
				updateMenuButtons();
			}
	});
	
}

/*
 * Benennt das betroffene Projekt nach dem angegebenen Namen um.
 * 
 * @param name neuer Name für das übergebene Projekt
 */
function renameProject(name) {
	
	documentsJsonRequest({
			'command': 'projectrename',
			'id': renameID,
			'name' : name
		}, function(result,data) {
			// wenn das ausgewählte Projekt erfolgreich umbenannt wurde, ist der Umbenennungs-Vorgang abgeschlossen
			if(result) {
				
				// setzt die Umbenennungs-IDs zurück
				renameID = null;
				prevName = null;
				
				// aktualisiert die Aktivierungen der Menü-Schaltflächen
				updateMenuButtons();
			}
			// wenn das ausgewählte Projekt für den übergebenen Namen nicht umbenannt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				treeInst.edit(renameID,"");
				
				// TEMP
				alert(data.response);
			}
	});
	
}

/*
 * Dupliziert das, der übergebenen ID entsprechende, Projekt unter dem angegebenen Namen.
 *
 * @param projectID ID des zu duplizierenden Projektes
 * @param name Name für das anzulegende Projekt
 */
function duplicateProject(projectID,name) {
	
	// dupliziert severseitig das, der übergebenen ID entsprechende, Projekte unter dem angegebenen Namen
	documentsJsonRequest({
			'command': 'projectclone',
			'id': projectID,
			'name': name
		}, function(result,data) {
			// wenn ein entsprechendes Projekt angelegt wurde, ist der Duplizierungs-Vorgang abgeschlossen
			if(result) {
				
				// übernimmt die Daten des angelegten Projektes in die angelegte Knoten-Komponente
				fillNode(duplicateNodeID,data.response);
				
				// setzt die Duplizierungs-IDs zurück
				duplicateNodeID = null;
				duplicateID = null;
				
				// aktualisiert die Aktivierungen der Menü-Schaltflächen (temporäre vollständige Deaktivierung wird aufgehoben)
				updateMenuButtons();
			}
			// wenn ein entsprechendes Projekt nicht angelegt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				treeInst.edit(duplicateNodeID,"");
				
				// TEMP
				alert(data.response);
			}
	});
	
}

/*
 * Exportiert ein Projekt als Zip und bietet diese zum Download an.
 * @param id ID des Projektes
 *
 */
function exportZip(id) {
    documentsRedirect({
        'command' : 'exportzip',
        'id' : treeInst.get_selected()[0],
        'name' : name
    }, function(result,data) {
        if(result) {
            console.log('Export Done!')
            }
        }
    );
}

/*
 *Importieren eines Projektes aus einer ZIP-Datei.
 *
 *
 */

/*
 * Fügt eine neue Knoten-Komponente anhand des übergebenen Projektes hinzu.
 * 
 * @param project Projekt, anhand dessen Daten eine neue Knoten-Komponente hinzugefügt werden soll
 */
function addNode(project) {
	
	// fügt eine neue Knoten-Komponente hinzu und füllt deren Attribute mit den Werten des übergebenen Projektes
	fillNode(treeInst.create_node("#",""),project);
}

/*
 * Füllt die Attribute der übergebenen Knoten-Komponente mit den Werten des angegebenen Projektes.
 * 
 * @param node ID der Knoten-Komponente, deren Attribute gemäß des angegebenen Projektes gesetzt werden sollen
 * @param porject Projekt, anhand dessen Daten die Attribute der übergebenen Knoten-Komponente gesetzt werden sollen
 */
function fillNode(nodeID,project) {
	
	node = treeInst.get_node(nodeID);
	
	// setzt die Bezeichnung der Knoten-Komponente auf den Namen des übergebenen Projektes
	treeInst.set_text(node,project.name);
	// setzt die ID der Knoten-Komponente auf die des übergebenen Projektes
	treeInst.set_id(node,project.id);
	
	// setzt die weiteren Attribute des Projektes
	node.author 	= project.author;
	node.createtime = project.createtime;
	node.rootid 	= project.rootid;
}

/*
 * Initialisiert die Anzeige der Projekte des Benutzers.
 */
function initProjects() {
	
	documentsJsonRequest({
			'command': 'listprojects'
		}, function(result,data) {
			if(result) {
				// legt für jedes Projekt eine Knoten-Komponente an
				for(var i=0; i<data.response.length; ++i)
					addNode(data.response[i]);
			}
	});
	
	// aktualisiert die Aktivierungen der Menü-Schaltflächen
	updateMenuButtons();
}

/*
 * Aktualisiert die Aktivierungen der Menü-Schaltflächen.
 */
function updateMenuButtons() {
	
	// flag für die Aktivierung der nicht-selektionsabhängigen Schaltflächen ('Erstellen' und 'Import')
	var basic;
	// flag für die Aktivierung der selektionsabhängigen Schaltflächen
	var remain;
	
	// Editierungsmodus
	if(creatingNodeID!=null || renameID!=null || duplicateID!=null) {
		// keine Aktivierungen
		basic  = false;
		remain = false;
	}
	// Selektion
	else if(selectedNodeID!="") {
		// vollständig Aktivierung
		basic  = true;
		remain = true;
	}
	else {
		// Aktivierung der nicht-selektionsabhängigen Schaltflächen
		basic  = true;
		remain = false;
	}
	
	// setzt die Aktivierungen der einzelnen Menü-Schaltflächen
	$('.projecttoolbar-open').prop("disabled", !remain);
	$('.projecttoolbar-new').prop("disabled", !basic);
	$('.projecttoolbar-delete').prop("disabled", !remain);
	$('.projecttoolbar-rename').prop("disabled", !remain);
	$('.projecttoolbar-duplicate').prop("disabled", !remain);
	$('.projecttoolbar-converttotemplate').prop("disabled", !remain);
	$('.projecttoolbar-export').prop("disabled", !remain);
	$('.projecttoolbar-import').prop("disabled", !basic);
}