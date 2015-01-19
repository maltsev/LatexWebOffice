/*
@author: Ingolf Bracht
@creation: 14.12.2014 - sprint-nr: 3
@last-change: 19.01.2014 - sprint-nr: 4
*/


var renameTemplateID = null;				// ID der derzeitig umzubenennenden Vorlage
var prevTemplateName = null;				// Name der derzeitig umzubenennenden Vorlage (für etwaiges Zurückbenennen)

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
		//console.log("AUTHOR: "+node.author+" ..... CREATETIME: "+node.createtime+" ..... ROOTID: "+node.id);

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

		

		// wenn der neue Name für eine bestehendes Vorlage bestätigt wurde
		if(renameTemplateID!=null) {

			// ... und kein oder derselbe Name eingegeben wurde, ...
			if(treeInst.get_text(renameTemplateID)==="" || treeInst.get_text(renameTemplateID)===prevTemplateName) {
				// ... wird der Umbenennungs-Vorgang abgebrochen
				//treeInst.set_text(renameTemplateID,prevTemplateName);
				node = treeInst.get_node(renameTemplateID);
				treeInst.set_text(node,getHTML(node));
				renameTemplateID = null;
				updateMenuButtons();
			}
			// ... und ein, vom bisherigen Namen verschiedener, Name eingegeben wurde, ...
			else
				// ... wird das serverseitige Umbenennen der betroffenen Vorlage eingeleitet
				renameTemplate(treeInst.get_text(renameTemplateID));
		}

	});

	// ----------------------------------------------------------------------------------------------------
	//                                             MENÜ-EINTRÄGE
	// ----------------------------------------------------------------------------------------------------

    //'Verwenden'-Schaltfläche
    $('templatestoolbar-use').on("click", function()) {
        templateToProject();
    });
    // 'Löschen'-Schaltfläche
	$('.templatestoolbar-delete').on("click", function() {

	});

	// 'Umbenennen'-Schaltfläche
	$('.templatestoolbar-rename').on("click", function() {

		node = treeInst.get_node(selectedNodeID);
		// Vorlage-ID der umzubenennenden Vorlage
		renameTemplateID = node.rootid;
		// derzeitiger Name der Vorlage (für etwaiges Zurückbenennen)
		prevTemplateName = node.templatename;

		// versetzt die Knoten-Komponente in den Bearbeitungsmodus
		editNode(renameTemplateID,node.templatename);

		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtons();

		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird renameTemplate() zum serverseitigen Umbenennen der betroffenen Vorlageaufgerufen

	});

	refreshTemplates();
});

// ----------------------------------------------------------------------------------------------------
//                                           FUNKTIONALITÄTEN
//                                      (client- und serverseitig)
// ----------------------------------------------------------------------------------------------------

/*
 * Eine Vorlage in ein Projekt umwandeln.
 */
function templateToProject(id,name,handler) {

	documentsJsonRequest({
		'command': 'template2project',
		'id': id,
		'name': name
		},
		function(result,data) {
			if(result) {
				document.location.assign('/dateien/#'+data.response.rootid);
				handler(true,'');
			} else
				handler(false,data.response);
	});
}

/*
 * Löscht ausgewählte Vorlage.
 */
function deleteTemplate() {

	documentsJsonRequest({
			'command': 'templaterm',
			'id': selectedNodeID
		},
		function(result,data) {
			if(result) {
				refreshTemplates();
				selectedNodeID = "";
			}
	});

}

/*
 * Umbenennen ausgewählte Vorlage
 */
function renameTemplate(name) {

	documentsJsonRequest({
			'command': 'templaterename',
			'id': renameTemplateID,
			'name' : name
		},
		function(result,data) {
			if(result) {
				renameTemplateID = null;
				prevTemplateName = null;
				refreshTemplates();
			}
			else {
				treeInst.edit(renameTemplateID,"");

				showPopover(treeInst.get_node(renameTemplateID),data.response);
			}
	});

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
 * @param nodeID ID der Knoten-Komponente, deren Attribute gemäß der angegebenen Vorlage gesetzt werden sollen
 * @param template Vorlage, anhand dessen Daten die Attribute der übergebenen Knoten-Komponente gesetzt werden sollen
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
		'command': 'listtemplates'
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
 */
function showPopover(node) {

	if(node!=null) {

		// Position der übergebenen Knoten-Komponente
		var pos = $('.node_item_'+node.id).position();
		var height = $('.node_item_'+node.id).height();

		// zeigt das Popover an und richtet es links über der Knoten-Komponente aus
		// (Reihenfolge nicht verändern!)
		$('.input_popover').popover('show');
        $('.popover').css('left',pos.left+'px');
        $('.popover').css('top',(pos.top-height*2+5)+'px');

	}
}

/*
 * Aktualisiert die Aktivierungen der Menü-Schaltflächen.
 */
function updateMenuButtons() {
    if(treeInst.get_selected().length!=0) {
		// vollständig Aktivierung
		basic  = true;
		remain = true;
	}


	// setzt die Aktivierungen der einzelnen Menü-Schaltflächen


	$('.templatestoolbar-delete').prop("disabled", !remain);
	$('.templatestoolbar-rename').prop("disabled", !remain);
	$('.templatestoolbar-use').prop("disabled", !remain);


}
