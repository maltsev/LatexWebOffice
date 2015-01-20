/*
@author: Ingolf Bracht
@creation: 14.12.2014 - sprint-nr: 3
@last-change: 14.12.2014 - sprint-nr: 3
*/

var renameID = null;
var prevName = null;

var selectedNodeID = "";
var prevSelectedNodeID 	= "";

var tree;
var treeInst;

/*
 * Initialisiert den JSTree und die Menü-Einträge.
 */
$(document).ready(function() {

	tree = $('.templateswrapper').jstree({"core"    : {"check_callback" : true,"multiple" : false},
										 "plugins" : ["state"]});

	/*
	 * Referenziert eine bestehende JSTree-Instanz (ohne eine neue zu erzeugen)
	 * (zu verwenden, um darauf knotenspezifische Methoden anzuwenden)
	 */
	treeInst = $('.templateswrapper').jstree();


	// Modal zum Bestätigen/Abbrechen des Löschvorgangs
	$('#modal_deleteConfirmation').on('hidden.bs.modal', function(e) {
		// fokussiert den JSTree, um nach Abbruch des Löschvorgangs Tasten-Events behandeln zu können
		tree.focus();
	});
	// 'Ja'-Button des Modals zur Bestätigung des Löschvorgangs
	$('.modal_deleteConfirmation_yes').on("click", function() {
		deleteTemplate();
	});

	// ----------------------------------------------------------------------------------------------------
	//                                               LISTENER                                              
	// ----------------------------------------------------------------------------------------------------
	
	// Auswahl-Listener
	tree.bind('select_node.jstree',function(e,data) {
		
		console.log("selection");
		
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
	
	// Tasten-Listener
	tree.bind('keydown',function(e) {
	
		// TEMP
		//console.log(e.keyCode);
		
		// Entf-Taste
		if(e.keyCode===46)
		$('#modal_deleteConfirmation').modal('show');
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Umbenennungs-Listener
	tree.bind('rename_node.jstree',function(e) {

		// blendet das Eingabe-Popover aus
		$('.input_popover').popover('hide');

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
		// wenn der neue Name für eine bestehende Vorlage bestätigt wurde (= Umbenennen)
		else if(renameID!=null) {

			// ... und kein oder derselbe Name eingegeben wurde, ...
			if(treeInst.get_text(renameID)==="" || treeInst.get_text(renameID)===prevName) {
				// ... wird der Umbenennungs-Vorgang abgebrochen
				//treeInst.set_text(renameID,prevName);
				node = treeInst.get_node(renameID);
				treeInst.set_text(node,getHTML(node));
				renameID = null;
				updateMenuButtons();
			}
			// ... und ein, vom bisherigen Namen verschiedener, Name eingegeben wurde, ...
			else
				// ... wird das serverseitige Umbenennen der betroffenen Vorlage eingeleitet
				renameTemplate(treeInst.get_text(renameID));
		}

	});

	// ----------------------------------------------------------------------------------------------------
	//                                             MENÜ-EINTRÄGE                                           
	// ----------------------------------------------------------------------------------------------------

	// 'Verwenden'-Schaltfläche
	$('.templatestoolbar-use').on("click", function() {
        templateToProject();
	});

	// 'Löschen'-Schaltfläche
	$('.templatestoolbar-delete').on("click", function() {

	});

	// 'Umbenennen'-Schaltfläche
	$('.templatestoolbar-rename').on("click", function() {

		node = treeInst.get_node(selectedNodeID);
		// Vorlage-ID der umzubenennenden Vorlage
		renameID = node.id;
		// derzeitiger Name der Vorlage (für etwaiges Zurückbenennen)
		prevName = node.templatename;

		// versetzt die Knoten-Komponente in den Bearbeitungsmodus
		editNode(renameID,node.templatename);

		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtons();

		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird renameTemplate() zum serverseitigen Umbenennen der betroffenen Vorlage aufgerufen

	});
});

// ----------------------------------------------------------------------------------------------------
//                                           FUNKTIONALITÄTEN                                          
//                                      (client- und serverseitig)                                     
// ----------------------------------------------------------------------------------------------------


/*Vorlage in ein Projekt umwandeln.
 *id(ID der Vorlage)
 *name(Name des zu erzeugenden Projektes)
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




//Löschen ausgewählter Vorlage.

function deleteTemplate() {

	documentsJsonRequest({
			'command': 'templaterm',
			'id': selectedNodeID
		}, function(result,data) {
			// wenn die ausgewählte Vorlage erfolgreich gelöscht wurde
			if(result) {

				// aktualisiert die Anzeige der Vorlagen
				refreshTemplates();

				// setzt die Selektions-ID zurück
				selectedNodeID = "";
			}
	});

}

//Umbenennen ausgewählter Vorlage.

function renameTemplate(name) {

	documentsJsonRequest({
			'command': 'templaterename',
			'id': renameID,
			'name' : name
		}, function(result,data) {
			// wenn die ausgewählte Vorlage erfolgreich umbenannt wurde, ist der Umbenennungs-Vorgang abgeschlossen
			if(result) {

				// setzt die Umbenennungs-IDs zurück
				renameID = null;
				prevName = null;

				// aktualisiert die Anzeige der Vorlagen
				refreshTemplates();
			}
			// wenn die ausgewählte vorlage für den übergebenen Namen nicht umbenannt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				treeInst.edit(renameID,"");

				// TEMP
				showPopover(treeInst.get_node(renameID),data.response);
			}
	});

}

/*
 * Fügt eine neue Knoten-Komponente anhand des übergebenen Projektes hinzu.
 *
 * @param project Projekt, anhand dessen Daten eine neue Knoten-Komponente hinzugefügt werden soll
 *
 * @return die ID der erzeugten Knoten-Komponente
 */
function addNode(project) {

	// fügt eine neue Knoten-Komponente hinzu und füllt die Attribute der Knoten-Komponente mit den Werten des übergebenen Projektes
	return fillNode(treeInst.create_node("#",""),project);
}

/*
 * Versetzt die, der übergebenen ID entsprechende, Knoten-Komponente in den Bearbeitungsmodus.
 *
 * @param nodeID ID der Knoten-Komponente, deren Name bearbeitet werden soll
 * @param text Text-Vorgabe zur Editierung
 */
function editNode(nodeID,text) {

	// zeigt das Eingabe-Popover in relativer Position zur betroffenen Knoten-Komponente an
	showPopover(treeInst.get_node(nodeID));
	// versetzt die betroffene Knoten-Komponente in den Bearbeitungsmodus
	treeInst.edit(nodeID,text);
}

/*
 * Füllt die Attribute der übergebenen Knoten-Komponente mit den Werten der angegebenen Vorlage.
 *
 * @param nodeID ID der Knoten-Komponente, deren Attribute gemäß des angegebenen Projektes gesetzt werden sollen
 * @param project Projekt, anhand dessen Daten die Attribute der übergebenen Knoten-Komponente gesetzt werden sollen
 *
 * @return die ID der Knoten-Komponente
 */
function fillNode(nodeID,template) {

	node = treeInst.get_node(nodeID);

	if(template!=null) {

		// setzt die ID der Knoten-Komponente auf die der übergebenen Vorlage
		treeInst.set_id(node,template.id);

		// setzt die weiteren Attribute der Vorlage
		node.templatename 		= template.name;
		node.author 			= template.ownername;
		node.createtime 		= template.createtime;
		node.rootid 			= template.rootid;

	}

	// setzt die Bezeichnung der Knoten-Komponente anhand der Daten der übergebenen Vorlage
	treeInst.set_text(node,getHTML(node));

	return node.id;
}

/*
 * Liefert die html-Repräsentation der übergebenen Knoten-Komponente.
 *
 * @param node Knoten-Komponente, deren zugehörige html-Repräsentation zurückgegeben werden soll
 *
 * @return die html-Repräsentation der übergebenen Knoten-Komponente
 */
function getHTML(node) {

	var relTime = getRelativeTime(node.createtime);

	return  "<div class=\"node_item\">"+
				"<li class=\"node_item_"+node.id+"\">"+
					"<span class=\"templateitem-name\">"+node.templatename+"</span>"+
					"<span class=\"templateitem-createdate\" title=\"erstellt "+relTime+"\">"+relTime+"</span>"+
		    		"<span class=\"templateitem-author\">"+node.author+"</span>"+
		    	"</li>"+
		    "</div>";
}

/*
 * Aktualisiert die Anzeige der Vorlagen des Benutzers.
 */
function refreshTemplates() {

	// leert den JSTrees
	treeInst.settings.core.data = null;
	treeInst.refresh();

	// aktualisiert den JSTree anhand der bestehenden Vorlagen
	documentsJsonRequest({
		'command': 'listtemplate'
		}, function(result,data) {
			if(result) {
				// legt für jede Vorlage eine Knoten-Komponente an
				for(var i=0; i<data.response.length; ++i)
					addNode(data.response[i]);
			}
	});

	// aktualisiert die Aktivierungen der Menü-Schaltflächen
	updateMenuButtons();
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
 * @param error Fehlermeldung, welche durch das Popover dargestellt werden soll
 */
function showPopover(node,error) {

	if(node!=null) {

		// Position der übergebenen Knoten-Komponente
		var pos = $('.node_item_'+node.id).position();
		var height = $('.node_item_'+node.id).height();

		var popover = $('.input_popover');
		if(error) {
			popover = $('.error_popover');
			popover.popover({content: error});
		}

		// zeigt das Popover an und richtet es links über der Knoten-Komponente aus
		// (Reihenfolge nicht verändern!)
		popover.popover('show');
        $('.popover').css('left',pos.left+'px');
        $('.popover').css('top',(pos.top-height*2+5)+'px');

	}
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
	if(renameID!=null) {
		// keine Aktivierungen
		basic  = false;
		remain = false;
	}
	// Selektion
	else if(treeInst.get_selected().length!=0) {
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

	$('.templatestoolbar-use').prop("disabled", !remain);
	$('.templatestoolbar-delete').prop("disabled", !remain);
	$('.templatestoolbar-rename').prop("disabled", !remain);

}