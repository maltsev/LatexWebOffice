/*
 * @author: Thore Thießen, Ingolf Bracht, Munzir Mohamed, Kirill Maltsev
 * @creation: 04.12.2014 - sprint-nr: 2
 * @last-change: 22.01.2015 - sprint-nr: 4
 */

var creatingNodeID = null;			// ID der Knoten-Komponente des derzeitig zu erstellenden Projektes
var renameID = null;				// ID des derzeitig umzubenennenden Projektes
var prevName = null;				// Name des derzeitig umzubenennenden Projektes (für etwaiges Zurückbenennen)
var deletingNodeID = null;			// ID des derzeitig zu löschenden Projektes
var duplicateNodeID = null;			// ID der Knoten-Komponente des derzeitig zu duplizierenden Projektes
var duplicateID = null;				// ID des derzeitig zu duplizierenden Projektes
var templatizedID = null;			// ID des derzeitig in eine Vorlage umzuwandelnden Projektes
var projectTempID = null;
var editMode = false;				// gibt an, ob sich eine der Knoten-Komponenten derzeitig im Editierungsmodus befindet

/*
 * Position und Höhe der selektierten Knoten-Komponente sind zu speichern,
 * da diese durch den Editierungsmodus temporär ihre html-Repräsentation verliert
 * und das zugehörige Objekt dadurch nicht mehr angesprochen werden kann,
 * um das Popover gemäß seiner Position und Höhe entsprechend auszurichten.
 */
var selectedHeight = 0;				// Höhe der selektierten Knoten-Komponente (zur Ausrichtung des Popovers)
var selectedPos = null;				// Position der selektierten Knoten-Komponente (zur Ausrichtung des Popovers)

var selectedNodeID = "";
var prevSelectedNodeID 	= "";

var allprojects=null; // Array von allen Projekten

var tree;
var treeInst;

var isProjectsPage = true; // false für die Seite mit Vorlagen;

/*
 * Initialisiert den JSTree und die Menü-Einträge.
 */
$(document).ready(function() {

    isProjectsPage = $(".templateswrapper").length === 0;
	
	tree = $('.projectswrapper').jstree({"core"    : {"check_callback" : true,"multiple" : false},
										 "plugins" : ["state"]});
	
	/*
	 * Referenziert eine bestehende JSTree-Instanz (ohne eine neue zu erzeugen)
	 * (zu verwenden, um darauf knotenspezifische Methoden anzuwenden)
	 */
	treeInst = $('.projectswrapper').jstree();
	
	
	// Modal zum Bestätigen/Abbrechen des Löschvorgangs
	$('#modal_deleteConfirmation').on('hidden.bs.modal', function(e) {
		// fokussiert den JSTree, um nach Abbruch des Löschvorgangs Tasten-Events behandeln zu können
		tree.focus();
	});
	// 'Ja'-Button des Modals zur Bestätigung des Löschvorgangs
	$('.modal_deleteConfirmation_yes').on("click", function() {
		deleteProject();
	})
	
	// Modal zur Eingabe eines Vorlagennamens ('in Vorlage umwandeln')
	$('#modal_projectToTemplate').on('hidden.bs.modal', function(e) {
		// fokussiert den JSTree, um nach Abbruch des Verwendens Tasten-Events behandeln zu können
		tree.focus();
	});
	// 'Bestätigen'-Button des Modals zur Bestätigung des Vorlagennamens
	$('.modal_projectToTemplate_confirm').on("click", function() {
		projectToTemplate($('#modal_projectToTemplate_tf').val());
	});

	// Modal zur Eingabe eines Projektsnamens ('in Projekt umwandeln')
     $('#modal_templateToProject').on('hidden.bs.modal', function(e) {
        // fokussiert den JSTree, um nach Abbruch des Verwendens Tasten-Events behandeln zu können
        tree.focus();
    });

    // 'Bestätigen'-Button des Modals zur Bestätigung des Projektsnamens
    $('.modal_templateToProject_confirm').on("click", function() {
        templateToProject($('#modal_templateToProject_tf').val());
    });
	$('.modal_share_confirm').on("click", function(e) {
		// Aktion nach Klicken des Share Buttons
		sendProjectInvitation(selectedNodeID,$('#modal_shareuser_tf').val());
	//	listInvitations();
	});
	$('.modal_deny_confirm').on("click", function(e) {
		// Aktion nach Klicken des deny Buttons
		
	});
	//VALIDATOR	
	//
	//falls versucht wird eine zip-datei zu importieren, die den gleichen namen hat, wie ein bestehendes projekt, muss der nutzer bestätigen, 
	//um das bestehende projekt zu überschreiben
	$('#files').change(function(){
		var file = $('#files')[0].files[0];
		var filename=file.name.substr(0,file.name.lastIndexOf('.'))||file.name; //versucht den Dateinamen ohne Dateiendung herauszufinden
	
		$('#checkboxdiv').addClass('hidden');	
		for (var i=0;i<allprojects.length;i++){
			var proj=allprojects[i].name;
			if (proj==filename){
				$('#overwritecheckbox').prop("checked", false);
				$('#checkboxdiv').removeClass('hidden');
			}
		}
	});

	// Aktiviere den validator auf das projektimport formular
	$('#projektimportposter').validate({
		rules:{
			files:{
				required:true,
			},
			overwritecheckbox:{
				required:true,
			}
		},
		messages:{
			overwritecheckbox: 'Ein Projekt mit gleichem Namen existiert schon'
		}
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
			
			selectedPos 	= $('.node_item_'+selectedNodeID).position();
			selectedHeight 	= $('.node_item_'+selectedNodeID).height();
			
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
		//console.log(e.keyCode);
		
		// Entf-Taste
		if(e.keyCode===46 && !editMode) {
			deletingNodeID = selectedNodeID;
			$('#modal_deleteConfirmation').modal('show');
		}
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Umbenennungs-Listener (für 'Erstellen' und 'Umbenennen')
	tree.bind('rename_node.jstree',function(e) {
		
		// blendet das Eingabe-Popover aus
		$('.input_popover').popover('hide');
		
		editMode = false;
		
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
		// wenn die Eingabe des Names eines zu duplizierenden Projektes bestätigt wurde (= Duplizieren eines Projektes), ...
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
				// ... wird das serverseitige Umbenennen des betroffenen Projektes eingeleitet
				renameProject(treeInst.get_text(renameID));
		}
		
	});
	
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
		creatingNodeID = addNode(null);
		// selektiert die erzeugte Knoten-Komponente
		selectNode(creatingNodeID);
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		editNode(creatingNodeID,"");
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen (vollständige Deaktivierung)
		updateMenuButtons();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird createProject() zum serverseitigen Erstellen eines entsprechenden Projektes aufgerufen
	});
	
	// 'Löschen'-Schaltfläche
	$('.projecttoolbar-delete').on("click", function() {
		
		deletingNodeID = selectedNodeID;
		
	});
	
	// 'Umbenennen'-Schaltfläche
	$('.projecttoolbar-rename').on("click", function() {
		
		node = treeInst.get_node(selectedNodeID);
		// Projekt-ID des umzubenennenden Projektes
		renameID = node.id;
		// derzeitiger Name des Projektes (für etwaiges Zurückbenennen)
		prevName = node.projectname;
		
		// versetzt die Knoten-Komponente in den Bearbeitungsmodus
		editNode(renameID,node.projectname);
		
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
		duplicateNodeID = addNode(null);
		// selektiert die erzeugte Knoten-Komponente
		selectNode(duplicateNodeID);
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		editNode(duplicateNodeID,"");
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen (vollständige Deaktivierung)
		updateMenuButtons();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird duplicateProject() zum serverseitigen Duplizieren eines entsprechenden Projektes aufgerufen		
		
	});
	
	// 'in Vorlage umwandeln'-Schaltfläche
	$('.projecttoolbar-converttotemplate').on("click", function() {
	
		// Projekt-ID des umzuwandelnden Projektes
		templatizedID = selectedNodeID;
		
		// öffnet das Modal zur Eingabe eines Vorlagennamens
		$('#modal_projectToTemplate').modal('show');
		
	});
	
	// 'Export'-Schaltfläche
	$('.projecttoolbar-export').on("click", function() {

		exportZip();
		
	});
	
	// 'Import'-Schaltfläche
	$('#projektimportposter').on('submit',function(event){
		var isvalidate=$("#projektimportposter").valid();
		if (isvalidate)
		{
			$('#projekt-import-modal').modal('hide')	//resette das Formular
			$('#checkboxdiv').addClass('hidden');	
			$('#overwritecheckbox').prop("checked", true);

			event.preventDefault();
			var form=new FormData(this);
			documentsJsonRequest(form,function(result,data){
				if (result)
					refreshProjects();
				else {
					$('#projectimporterrorbody').html(data.response);
					$('#projectimporterror').modal('show');
				}
			},false,false);
			this.reset();
			$('#projektimportposter>div').removeClass('has-success');
		}


	});

	// 'Verwenden'-Schaltfläche
	$('.templatestoolbar-use').on("click", function() {
        projectTempID = node.id;
        $('#modal_templateToProject').modal('show');
	});
	
	


	refreshProjects();
	
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
 * Sendet an die übergebene E-Mail Adresse eines Nutzers eine Mail, um ihn für ein Projekt einzuladen.
 * @param projectId - Die Id des Projektes, für das der Nutzer eingeladen wird
 * @param email - E-Mail Adresse des eingeladenen Nutzers
 */
function sendProjectInvitation(projectId,email) {
	
	documentsJsonRequest({
			'command': 'inviteuser',
			'name': email,
			'id':projectId
		}, function(result,data) {
			if(result) {
				alert("Result"+result);
			}
			else {
				alert(data.response);
			}
	});
}

/*
 * Aktualisiert die Anzeige der Projekte des Benutzers.
 */
function listInvitations() {
	
	// leert den JSTrees
	treeInst.settings.core.data = null;
	treeInst.refresh();
	
	// aktualisiert den JSTree anhand der bestehenden Projekte
	documentsJsonRequest({
		'command': 'listunconfirmedcollaborativeprojects'
		}, function(result,data) {
			if(result) {
				allprojects=data.response;
				// legt für jedes Projekt eine Knoten-Komponente an
				for(var i=0; i<data.response.length; ++i)
					addNode(data.response[i]);
			}
	});
	
	// aktualisiert die Aktivierungen der Menü-Schaltflächen
	updateMenuButtons();
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
				
				// setzt die Erstellungs-ID zurück
				creatingNodeID = null;
				
				// aktualisiert die Anzeige der Projekte
				refreshProjects();
				
				// aktualisiert die Aktivierungen der Menü-Schaltflächen (temporäre vollständige Deaktivierung wird aufgehoben)
				//updateMenuButtons();
			}
			// wenn ein entsprechendes Projekt nicht angelegt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				node = treeInst.get_node(creatingNodeID);
				treeInst.set_text(node,getHTML(node));
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
			'command': isProjectsPage ? 'projectrm' : 'templaterm',
			'id': deletingNodeID
		}, function(result,data) {
			// wenn das ausgewählte Projekt erfolgreich gelöscht wurde
			if(result) {
				
				// entfernt die zugehörige Knoten-Komponente
				treeInst.delete_node(selectedNodeID);
				
				// setzt die Löschung-ID zurück
				deletingNodeID = null;
				// setzt die Selektions-ID zurück
				selectedNodeID = "";
				
				// aktualisiert die Aktivierungen der Menü-Schaltflächen
				updateMenuButtons();
				refreshProjects();	
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
			'command': isProjectsPage ? 'projectrename' : 'templaterename',
			'id': renameID,
			'name' : name
		}, function(result,data) {
			// wenn das ausgewählte Projekt erfolgreich umbenannt wurde, ist der Umbenennungs-Vorgang abgeschlossen
			if(result) {
				
				// setzt die Umbenennungs-IDs zurück
				renameID = null;
				prevName = null;
				
				// aktualisiert die Anzeige der Projekte
				refreshProjects();
			}
			// wenn das ausgewählte Projekt für den übergebenen Namen nicht umbenannt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				treeInst.edit(renameID,"");
				
				// TEMP
				alert(data.response);
				//showPopover(treeInst.get_node(renameID),data.response);
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
				
				// setzt die Duplizierungs-IDs zurück
				duplicateNodeID = null;
				duplicateID = null;
				
				// aktualisiert die Anzeige der Projekte
				refreshProjects();
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
 * Wandelt das momentan ausgewählte Projekt in eine Vorlage um.
 *
 * @param name Name für die zu erzeugende Vorlage
 */ 
function projectToTemplate(name) {
	
	// wandelt severseitig das, der übergebenen ID entsprechende, Projekt in eine Vorlage unter dem angegebenen Namen um
	documentsJsonRequest({
			'command': 'project2template',
			'id': templatizedID,
			'name': name
		}, function(result,data) {
			// wenn eine entsprechende Vorlage angelegt wurde, ist der Umwandlungs-Vorgang abgeschlossen
			if(result) {
				
				// setzt die Umwandlungs-IDs zurück
				templatizedID = null;
				
				// Weiterleitung zu Vorlagen
				document.location.assign('/vorlagen/');
			}
			// wenn eine entsprechende Vorlage nicht angelegt werden konnte, ...
			else {
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
function exportZip() {
    documentsRedirect({
        'command' : 'exportzip',
        'id' : treeInst.get_node(prevSelectedNodeID).rootid,

    }, function(result,data) {
        if(result) {
            console.log('Export Done!')
            }
        }
    );
}

/*
 * Wandelt eine Vorlage in ein Projekt um
 * id (ID der Vorlage, aus der ein Projekt erzeugt wird)
 * name (Name des zu erzeugenden Projektes, dies darf nicht mit einem vorhandenen Projekt übereinstimmen)
 */
function templateToProject(name) {
	documentsJsonRequest({
            'command': 'template2project',
            'id': projectTempID,
            'name': name
        },

        function(result,data) {
			if(result) {
			    projectTempID = null;
				// Weiterleitung zum erzeugten Projekt
				document.location.assign('/projekt/');

			} else {
				alert(data.response);
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
	
	editMode = true;
	
	// zeigt das Eingabe-Popover in relativer Position zur betroffenen Knoten-Komponente an
	showPopover(treeInst.get_node(nodeID));
	// versetzt die betroffene Knoten-Komponente in den Bearbeitungsmodus
	treeInst.edit(nodeID,text);
}

/*
 * Füllt die Attribute der übergebenen Knoten-Komponente mit den Werten des angegebenen Projektes.
 * 
 * @param nodeID ID der Knoten-Komponente, deren Attribute gemäß des angegebenen Projektes gesetzt werden sollen
 * @param project Projekt, anhand dessen Daten die Attribute der übergebenen Knoten-Komponente gesetzt werden sollen
 *
 * @return die ID der Knoten-Komponente
 */
function fillNode(nodeID,project) {
	
	node = treeInst.get_node(nodeID);
	
	if(project!=null) {
		
		// setzt die ID der Knoten-Komponente auf die des übergebenen Projektes
		treeInst.set_id(node,project.id);
		
		// setzt die weiteren Attribute des Projektes
		node.projectname 		= project.name;
		node.author 			= project.ownername;
		node.createtime 		= project.createtime;
		node.rootid 			= project.rootid;
		
	}
	
	// setzt die Bezeichnung der Knoten-Komponente anhand der Daten des übergebenen Projektes
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
					"<span class=\"fadeblock projectitem-name\">"+node.projectname+"</span>"+
					"<span class=\"projectitem-createdate\" title=\"erstellt "+relTime+"\">"+relTime+"</span>"+
		    		"<span class=\"projectitem-author\">"+node.author+"</span>"+
		    	"</li>"+
		    "</div>";
}

/*
 * Aktualisiert die Anzeige der Projekte des Benutzers.
 */
function refreshProjects() {
	
	// leert den JSTrees
	treeInst.settings.core.data = null;
	treeInst.refresh();
	
	// aktualisiert den JSTree anhand der bestehenden Projekte
	documentsJsonRequest({
		'command': isProjectsPage ? 'listprojects' : 'listtemplates',
		}, function(result,data) {
			if(result) {
				allprojects=data.response;
				// legt für jedes Projekt eine Knoten-Komponente an
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
	
	selectedPos 	= $('.node_item_'+selectedNodeID).position();
	selectedHeight 	= $('.node_item_'+selectedNodeID).height();
}

/*
 * Zeigt das Popover in relativer Position zur übergebenen Knoten-Komponente an.
 *
 * @param node Knoten-Komponente zu deren Position das Popover relativ angezeigt werden soll
 * @param error Fehlermeldung, welche durch das Popover dargestellt werden soll
 */
function showPopover(node,error) {
	
	if(node!=null) {
		
		var popover = $('.input_popover');
		
		// zeigt das Popover an und richtet es links über der Knoten-Komponente aus
		// (Reihenfolge nicht verändern!)
		popover.popover('show');
        $('.popover').css('left',selectedPos.left+'px');
        $('.popover').css('top',(selectedPos.top-43)+'px');
		
		/*
		// Position der übergebenen Knoten-Komponente	
		var pos = $('.node_item_'+node.id).position();
		var height = $('.node_item_'+node.id).height();
		
		var popover = $('.input_popover');;
		if(error) {
			popover = $('.error_popover');
			popover.popover({content: error});
		}
		
		// zeigt das Popover an und richtet es links über der Knoten-Komponente aus
		// (Reihenfolge nicht verändern!)
		popover.popover('show');
        $('.popover').css('left',selectedPos.left+'px');
        $('.popover').css('top',(selectedPos.top-selectedHeight*2+5)+'px');
        }
        console.log($('.popover').css('height'));
        */
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
	if(creatingNodeID!=null || renameID!=null || duplicateID!=null) {
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
	$('.projecttoolbar-open').prop("disabled", !remain);
	$('.projecttoolbar-new').prop("disabled", !basic);
	$('.projecttoolbar-delete').prop("disabled", !remain);
	$('.projecttoolbar-rename').prop("disabled", !remain);
	$('.projecttoolbar-duplicate').prop("disabled", !remain);
	$('.projecttoolbar-converttotemplate').prop("disabled", !remain);
	$('.projecttoolbar-export').prop("disabled", !remain);
	$('.projecttoolbar-import').prop("disabled", !basic);
	$('.projecttoolbar-share').prop("disabled", !remain);
	$('.projecttoolbar-deny').prop("disabled", !remain);
	$('.templatestoolbar-use').prop("disabled", !remain);
}
