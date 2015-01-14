/*
@author: Timo Dümke, Ingolf Bracht
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 14.01.2015 - sprint-nr: 4
*/

// ID der Knoten-Komponente des derzeitig zu erstellenden Projektes
var creatingNodeID = null;
// ID des vorliegenden Projektes
var projectID;
// ID der momentan ausgewählten Knoten-Komponente
var selectedNodeID = "";

/*
 * Referenziert eine bestehende JSTree-Instanz (ohne eine neue zu erzeugen)
 * (zu verwenden, um darauf knotenspezifische Methoden anzuwenden)
 */
var treeInst;

/*
 * Initialisiert den JSTree sowie die Menü-Einträge und listet die Verzeichnisstruktur auf.
 */
$(document).ready(function() {

	// ermittelt die Projekt-ID aus der URL
	projectID = parseInt(location.hash.substr(1));
	
	/*
	 * Erzeugt eine neue JSTree-Instanz
	 * (zu verwenden, um darauf instanz-spezifische Methoden (z.B. für Listener) anzuwenden)
	 *
	 * Plugins:	'state' zum browser-seitigen Speichern der geöffneten und ausgewählten Knoten-Komponenten
	 * 					(notwendig, da beim Aktualisieren der Seite die Auswahl verloren geht, die Menü-Einträge jedoch ggf. aktiviert bleiben)
	 */
	var tree = $('.projectswrapper').jstree({"core"    : {"check_callback" : true,"multiple" : false},
											 "plugins" : ["dnd","state"]});
	
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
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Doppelklick-Listener
	tree.bind("dblclick.jstree",function(e) {
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Tasten-Listener
	tree.bind('keydown',function(e) {
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// wenn eine ungültige Projekt-ID vorliegt, ...
	if(isNaN(projectID)) {
		// ... wird zur Projekt-Übersicht weitergeleitet
		backToProject();
	}
	// wenn eine gültige Projekt-ID vorliegt, ...
	else {
		// ... wird die Anzeige der Dateien und ihrer Verzeichnisstruktur des zugehörigen Projektes initialisiert
		initFiles();
	}
	
	// ----------------------------------------------------------------------------------------------------
	//                                             MENÜ-EINTRÄGE                                           
	// ----------------------------------------------------------------------------------------------------
	
	// 'Öffnen'-Schaltfläche
	$('.filestoolbar-open').on("click", function() {
		
		// TODO
		
	});
	
	// 'Erstellen'-Schaltfläche
	$('.filestoolbar-new').on("click", function() {
		
		// TODO
		
	});
	
	// 'Löschen'-Schaltfläche
	$('.filestoolbar-delete').on("click", function() {
		
		// TODO
		
	});
	
	// 'Umbenennen'-Schaltfläche
	$('.filestoolbar-rename').on("click", function() {
		
		// TODO
		
	});
	
	// 'Verschieben'-Schaltfläche
	$('.filestoolbar-move').on("click", function() {
		
		// TODO
		
	});
	
	// 'Herunterladen'-Schaltfläche
	$('.filestoolbar-download').on("click", function() {
		
		// TODO
		
	});
	
	// 'Hochladen'-Schaltfläche
	$('.filestoolbar-upload').on("click", function() {
		
		// TODO
		
	});

});




/*
 * Leitet den Benutzer zurück zur Projektverwaltung.
 */
function backToProject() {
	// TODO: auf das richtige Projekt verweisen?
	window.location.replace('/projekt/');
}

/*
 * Initialisiert die Anzeige der Dateien und ihrer Verzeichnisstruktur des Benutzers.
 */
function initFiles() {
	
	documentsJsonRequest({
			'command': 'listfiles',
			'id': projectID
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
	
	// flag für die Aktivierung der nicht-selektionsabhängigen Schaltflächen ('Erstellen' und 'Hochladen')
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
	$('.filestoolbar-open').prop("disabled", !remain);
	$('.filestoolbar-new').prop("disabled", !basic);
	$('.filestoolbar-delete').prop("disabled", !remain);
	$('.filestoolbar-rename').prop("disabled", !remain);
	$('.filestoolbar-move').prop("disabled", !remain);
	$('.filestoolbar-download').prop("disabled", !remain);
	$('.filestoolbar-upload').prop("disabled", !basic);
}