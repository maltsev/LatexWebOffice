/*
 * @author: Thore Thießen
 * @coauthor: Ingolf Bracht
 * @creation: 04.12.2014 - sprint-nr: 2
 * @last-change: 11.01.2015 - sprint-nr: 4
 */

// speichert die ID der Knoten-Komponente des derzeitig zu erstellenden Projektes
var creatingNodeID = null;

var prevSelectedNodeID 	= "";

/*
 * Initialisiert den JSTree und die Menü-Einträge.
 */
$(document).ready(function() {
	
	var selectedNodeID 		= "";
	
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
											 "plugins" : ["dnd","state"]});
	
	/*
	 * Referenziert eine bestehende JSTree-Instanz (ohne eine neue zu erzeugen)
	 * (zu verwenden, um darauf knotenspezifische Methoden anzuwenden)
	 */
	var treeInst = $('.projectswrapper').jstree();
	
	
	// ----------------------------------------------------------------------------------------------------
	//                                               LISTENER                                              
	// ----------------------------------------------------------------------------------------------------
	
	// Auswahl-Listener
	tree.bind('select_node.jstree',function(e,data) {
		
		console.log('selected: '+data.node.id);
		
		// Deselektion (die der Selection-ID zugehörige Knoten-Komponente wurde erneut selektiert)
		if(selectedNodeID===data.node.id) {
			
			// deaktiviert die selektionsabhängigen Schaltflächen (=> 'Erstellen' und 'Import' bleiben aktiviert)
			setMenuButtonsEnabled(false,false);
			
			// deselektiert die betroffene Knoten-Komponente
			treeInst.deselect_node(data.node);
			// setzt die Selection-ID zurück
			selectedNodeID = "";
			
		}
		// Selektion (eine Knoten-Komponente werde selektiert, deren ID nicht mit der Selection-ID übereinstimmt)
		else {
			
			// wenn zuvor keine Knoten-Komponenten ausgewählt war (Aktivierung von Schaltflächen notwendig), ...
			if(selectedNodeID==="") {
				// ... werden sämtliche Schaltflächen aktiviert
				setMenuButtonsEnabled(true,true);
			}
			
			// aktualisiert die Selection-ID gemäß der ausgewählten Knoten-Komponente
			selectedNodeID = data.node.id;
			prevSelectedNodeID = data.node.id;
			
		}
		
		node = data.instance.get_node(data.selected[0]);
		
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
    	      	
			// Escape-Taste (Abbruch 'Erstellen' bzw. 'Umbenennen')
			case 27:
				
				// setzt die Erstellungs-ID zurück
				//creatingNodeID = null;
				console.log("ESCAPE!!!!");
				
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
		
		// wenn der Name eines neuen Projektes bestätigt wurde (= Erstellen)
		if(creatingNodeID!=null) {
			// erzeugt severseitig ein neues Projekt mit dem festgelegten Namen
			createProject(treeInst.get_text(creatingNodeID));
		}
		// wenn der neue Name für ein bestehendes Projekt bestätigt wurde (= Umbenennen)
		else {
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
		
		var treeInst = $('.projectswrapper').jstree();
		
		// erzeugt eine neue Knoten-Komponente
		creatingNodeID = treeInst.create_node("#","neues Projekt");
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		treeInst.edit(creatingNodeID,"");
		
		// deaktiviert temporär sämtliche Menü-Schaltflächen
		setMenuButtonsEnabled(false,true);
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird createProject() zum serverseitigen Erstellen eines entsprechenden Projektes aufgerufen
	});
	
	// 'Löschen'-Schaltfläche
	$('.projecttoolbar-delete').on("click", function() {
		
		deleteProject();
		
	});
	
	// 'Umbenennen'-Schaltfläche
	$('.projecttoolbar-rename').on("click", function() {
		
		renameProject();
		
		// TEMP
		console.log('umbenennen');
		
		// TODO
		
	});
	
	// 'Duplizieren'-Schaltfläche
	$('.projecttoolbar-duplicate').on("click", function() {
		
		// TEMP
		console.log('duplizieren');
		
		// TODO
		
	});
	
	// 'in Vorlage umwandeln'-Schaltfläche
	$('.projecttoolbar-converttotemplate').on("click", function() {
		
		// TEMP
		console.log('in Vorlage umwandeln');
		
		// TODO
		
	});
	
	// 'Export'-Schaltfläche
	$('.projecttoolbar-export').on("click", function() {
		
		// TEMP
		console.log('export');
		
		// TODO
		
	});
	
	// 'Import'-Schaltfläche
	$('.projecttoolbar-import').on("click", function() {
		
		// TEMP
		console.log('import');
		
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
			// wenn ein entsprechendes Projekt erstellt wurde, ...
			if(result) {
				// ... ist der Erstellungs-Vorgang abgeschlossen und die Erstellungs-ID wird zurückgesetzt
				creatingNodeID = null;
				// TEMP
				console.log('Projekt erfolgreich erstellt');
			}
			// wenn ein entsprechendes Projekt nicht angelegt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				$('.projectswrapper').jstree().edit(creatingNodeID,"");
				// TEMP
				console.log(data.response);
			}
	});
	
	
}

/*
 * Löscht das momentan ausgewählte Projekt.
 */
function deleteProject() {
	
	var treeInst = $('.projectswrapper').jstree();
	
	documentsJsonRequest({
			'command': 'projectrm',
			'id': treeInst.get_selected()[0]
		}, function(result,data) {
			// wenn das ausgewählte Projekt erfolgreich gelöscht wurde, ...
			if(result) {
				
				// ... wird die zugehörige Knoten-Komponente entfernt
				treeInst.delete_node(treeInst.get_selected()[0]);
				selectedNodeID = "";
				
				// deaktiviert die selektionsabhängigen Schaltflächen (=> 'Erstellen' und 'Import' bleiben aktiviert)
				setMenuButtonsEnabled(false,false);
			}
	});
	
}

/*
 * Benennt das übergebene Projekt nach dem angegebenen Namen um.
 *
 * @param project Projekt, welches umbenannt werden soll
 * @param name neuer Name für das übergebene Projekt
 *
 */
function renameProject() {
	
	var treeInst = $('.projectswrapper').jstree();
	
	// versetzt die ausgewählte Knoten-Komponente in den Bearbeitungsmodus
	treeInst.edit(treeInst.get_selected());
	
	// TODO
	
}



/*
 * Setzt die Aktivierung sämtlicher Menü-Schaltflächen.
 *
 * @param enabled <code>true</code>, um die Menü-Schaltflächen zu aktivieren - <code>false</code>, um sie zu deaktivieren
 * @param strict <code>true</code>, um die Aktivierung sämtlicher Menü-Schaltflächen zu setzen -
 *               <code>false</code>, um die nicht von einer konkreten Selektion abhängigen Schaltflächen ('Erstellen' und 'Import') unbetrachtet zu lassen
 */
function setMenuButtonsEnabled(enabled,strict) {
	
	$('.projecttoolbar-open').prop("disabled", !enabled);
	$('.projecttoolbar-delete').prop("disabled", !enabled);
	$('.projecttoolbar-rename').prop("disabled", !enabled);
	$('.projecttoolbar-duplicate').prop("disabled", !enabled);
	$('.projecttoolbar-converttotemplate').prop("disabled", !enabled);
	$('.projecttoolbar-export').prop("disabled", !enabled);
	
	if(strict) {
		$('.projecttoolbar-new').prop("disabled", !enabled);
		$('.projecttoolbar-import').prop("disabled", !enabled);
	}
}
/**
 * Initialisiert die Anzeige der Projekte des Benutzers.
 */
function initProjects() {
	
	var treeInst = $('.projectswrapper').jstree();
	
	documentsJsonRequest({
			'command': 'listprojects'
		}, function(result,data) {
			if(result) {
				// legt für jedes Projekt eine Knoten-Komponente an
				for(var i=0; i<data.response.length; ++i) {
					var node = treeInst.create_node("#",data.response[i].name);
					treeInst.set_id(node,data.response[i].id);
					//console.log("--------------"+treeInst.get_node(node).attr("id"));
					//node.data("author","");
					//node.attr("createdate",data.response[i].createtime);
					//node.attr("rootid",data.response[i].rootid);
				}
			}
	});
	
	// deaktiviert die selektionsabhängigen Schaltflächen (=> 'Erstellen' und 'Import' bleiben aktiviert)
	setMenuButtonsEnabled(false,false);
}