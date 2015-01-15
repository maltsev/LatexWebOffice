/*
 * @author: Thore Thießen, Ingolf Bracht, Munzir Mohamed
 * @creation: 04.12.2014 - sprint-nr: 2
 * @last-change: 15.01.2015 - sprint-nr: 4
 */

// speichert die ID der Knoten-Komponente des derzeitig zu erstellenden Projektes
var creatingNodeID = null;

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
											 "data"    : {"attr": {
											 					"author" : "",
														  		"createdate" : "",
														  		"rootid" : ""}},
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
		console.log(e.keyCode);
		
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
				console.log("here");
				// ... wird das Erstellungs-Vorgang abgebrochen
				treeInst.delete_node(creatingNodeID);
				creatingNodeID = null;
				updateMenuButtons();
			}
			// ... und ein Name eingegeben wurde, ...
			else
				// ... wird severseitig ein neues Projekt mit dem festgelegten Namen erzeugt
				createProject(treeInst.get_text(creatingNodeID));
		}
		// wenn der neue Name für ein bestehendes Projekt bestätigt wurde (= Umbenennen)
		else {
			// benennt das betroffene Projekt serverseitig um
			renameProject(treeInst.get_selected().name);
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
		
		// versetzt die ausgewählte Knoten-Komponente in den Bearbeitungsmodus
		treeInst.edit(treeInst.get_selected());
		
		renameProject();
		
	});
	
	// 'Duplizieren'-Schaltfläche
	$('.projecttoolbar-duplicate').on("click", function() {
		
		// TODO
		
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
	
	// TODO (project.rootid statt der mit der Knoten-ID übereinstimmenden project.id)
	document.location.assign('/dateien/#' + prevSelectedNodeID);
	
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
 * Benennt das übergebene Projekt nach dem angegebenen Namen um.
 * 
 * @param name neuer Name für das übergebene Projekt
 *
 */
function renameProject(name) {
	
	/*
	documentsJsonRequest({
			'command': 'projectrm',
			'id': treeInst.get_selected()[0],
			'name' : name
		}, function(result,data) {
			// wenn das ausgewählte Projekt erfolgreich umbenannt wurde, ist der Umbenennungs-Vorgang abgeschlossen
			if(result) {
				console.log('Umbenennung erfolgreich');
			}
			// wenn das ausgewählte Projekt für den übergebenen Namen nicht umbenannt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				treeInst.edit(treeInst.get_selected()[0],"");
				
				// TEMP
				alert(data.response);
			}
	});
	*/
	
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
 * @param node Knoten-Komponente, deren Attribute gemäß des angegebenen Projektes gesetzt werden sollen
 * @param porject Projekt, anhand dessen Daten die Attribute der übergebenen Knoten-Komponente gesetzt werden sollen
 */
function fillNode(node,project) {
	
	// setzt die Bezeichnung der Knoten-Komponente auf den Namen des übergebenen Projektes
	treeInst.set_text(node,project.name);
	// setzt die ID der Knoten-Komponente auf die des übergebenen Projektes
	treeInst.set_id(node,project.id);
	
	// TODO
	// setzt die weiteren Attribute des Projektes
	//node.data("author","");
	//node.attr("createdate",data.response[i].createtime);
	//node.attr("rootid",data.response[i].rootid);
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
	if(creatingNodeID!=null) {
		// keine Aktivierungen
		basic  = false;
		remain = false;
	}
	// Selektion
	else if(selectedNodeID!="") {
		console.log("select");
		// vollständig Aktivierung
		basic  = true;
		remain = true;
	}
	else {
		console.log("deselect");
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