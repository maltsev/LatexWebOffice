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
var currentAuthor = user;
var number_of_invitedusers = 0;
/*
 * Position und Höhe der selektierten Knoten-Komponente sind zu speichern,
 * da diese durch den Editierungsmodus temporär ihre html-Repräsentation verliert
 * und das zugehörige Objekt dadurch nicht mehr angesprochen werden kann,
 * um das Popover gemäß seiner Position und Höhe entsprechend auszurichten.
 */
var selectedHeight = 0;				// Höhe der selektierten Knoten-Komponente (zur Ausrichtung des Popovers)
var selectedPos = null;				// Position der selektierten Knoten-Komponente (zur Ausrichtung des Popovers)
var selectedNodeIDProjects = "";
var selectedNodeIDInvitations = "";
var prevSelectedNodeID 	= "";

var allprojects=null; // Array von allen Projekten

var treeProjects;
var treeInvitations;
var treeInstInvitations;
var treeInstProjects;

var isProjectsPage = true; // false für die Seite mit Vorlagen;

/*
 * Initialisiert den JSTree und die Menü-Einträge.
 */
$(document).ready(function() {

    isProjectsPage = $(".templateswrapper").length === 0;
	
	treeProjects = $('.projectswrapper').jstree({"core"    : {"check_callback" : true,"multiple" : false},
										 "plugins" : ["state"]});
	treeInvitations = $('.invitationswrapper').jstree({"core"    : {"check_callback" : true,"multiple" : false},
										 "plugins" : ["state"]});
	/*
	 * Referenziert eine bestehende JSTree-Instanz (ohne eine neue zu erzeugen)
	 * (zu verwenden, um darauf knotenspezifische Methoden anzuwenden)
	 */
	treeInstProjects = $('.projectswrapper').jstree();
	treeInstInvitations = $('.invitationswrapper').jstree();
	
	// Modal zum Bestätigen/Abbrechen des Löschvorgangs
	$('#modal_deleteConfirmation').on('hidden.bs.modal', function(e) {
		// fokussiert den JSTree, um nach Abbruch des Löschvorgangs Tasten-Events behandeln zu können
		treeProjects.focus();
	});
	// 'Ja'-Button des Modals zur Bestätigung des Löschvorgangs
	$('.modal_deleteConfirmation_yes').on("click", function() {
		deleteProject();
	})
	
	// Modal zur Eingabe eines Vorlagennamens ('in Vorlage umwandeln')
	$('#modal_projectToTemplate').on('hidden.bs.modal', function(e) {
		// fokussiert den JSTree, um nach Abbruch des Verwendens Tasten-Events behandeln zu können
		treeProjects.focus();
	});
	// 'Bestätigen'-Button des Modals zur Bestätigung des Vorlagennamens
	$('.modal_projectToTemplate_confirm').on("click", function() {
		projectToTemplate($('#modal_projectToTemplate_tf').val());
	});

	// Modal zur Eingabe eines Projektsnamens ('in Projekt umwandeln')
     $('#modal_templateToProject').on('hidden.bs.modal', function(e) {
        // fokussiert den JSTree, um nach Abbruch des Verwendens Tasten-Events behandeln zu können
        treeProjects.focus();
    });

    // 'Bestätigen'-Button des Modals zur Bestätigung des Projektsnamens
    $('.modal_templateToProject_confirm').on("click", function() {
        templateToProject($('#modal_templateToProject_tf').val());
    });
	$('.modal_share_confirm').on("click", function(e) {
		// Aktion nach Klicken des Share Buttons
		sendProjectInvitation(selectedNodeIDProjects,$('#modal_shareuser_tf').val());
	});
	$('.modal_deny_confirm').on("click", function(e) {
		// Aktion nach Klicken des deny Buttons
		$("input:checkbox[name=denyProjectAccess]:checked").each(function()
		{		
		var user = $(this).val();
		denyProjectAccess(selectedNodeIDProjects,user);
});
	});
		$('.modal_quitCollaboration_confirm').on("click", function(e) {
		// Aktion nach Klicken des deny Buttons
		currentAuthor = user;
		quitCollaboration();
	

		//
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
	treeProjects.bind('select_node.jstree',function(e,data) {
		
		// Deselektion (die der Selection-ID zugehörige Knoten-Komponente wurde erneut selektiert)
		if(selectedNodeIDProjects===data.node.id) {
			
			// deselektiert die betroffene Knoten-Komponente
			treeInstProjects.deselect_node(data.node);
			// setzt die Selection-ID zurück
			selectedNodeIDProjects = "";
			
		}
		// Selektion (eine Knoten-Komponente werde selektiert, deren ID nicht mit der Selection-ID übereinstimmt)
		else {
			
			// aktualisiert die Selection-ID gemäß der ausgewählten Knoten-Komponente
			selectedNodeIDProjects = data.node.id;
			currentAuthor = data.node.author;
			prevSelectedNodeID = data.node.id;
			
			selectedPos 	= $('.node_item_'+selectedNodeIDProjects).position();
			selectedHeight 	= $('.node_item_'+selectedNodeIDProjects).height();
			
		}
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtonsProject();
	});
	
	// Auswahl-Listener
	treeInvitations.bind('select_node.jstree',function(e,data) {
		
		// Deselektion (die der Selection-ID zugehörige Knoten-Komponente wurde erneut selektiert)
		if(selectedNodeIDInvitations===data.node.id) {
			
			// deselektiert die betroffene Knoten-Komponente
			treeInstInvitations.deselect_node(data.node);
			// setzt die Selection-ID zurück
			selectedNodeIDInvitations = "";
			
		}
		// Selektion (eine Knoten-Komponente werde selektiert, deren ID nicht mit der Selection-ID übereinstimmt)
		else {
			
			// aktualisiert die Selection-ID gemäß der ausgewählten Knoten-Komponente
			selectedNodeIDInvitations = data.node.id;
			prevSelectedNodeID = data.node.id;
			
			selectedPos 	= $('.node_item_'+selectedNodeIDInvitations).position();
			selectedHeight 	= $('.node_item_'+selectedNodeIDInvitations).height();
			
		}
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtonsInvitation();
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Doppelklick-Listener
	treeProjects.bind("dblclick.jstree",function(e) {
		
		openProject();
		
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Tasten-Listener
	treeProjects.bind('keydown',function(e) {
		
		// TEMP
		//console.log(e.keyCode);
		
		// Entf-Taste
		if(e.keyCode===46 && !editMode) {
			deletingNodeID = selectedNodeIDProjects;
			$('#modal_deleteConfirmation').modal('show');
		}
	});
	
	// ----------------------------------------------------------------------------------------------------
	
	// Umbenennungs-Listener (für 'Erstellen' und 'Umbenennen')
	treeProjects.bind('rename_node.jstree',function(e) {
		
		// blendet das Eingabe-Popover aus
		$('.input_popover').popover('hide');
		
		editMode = false;
		
		// wenn die Eingabe des Namens eines neuen Projektes bestätigt wurde (= Erstellen eines Projektes), ...
		if(creatingNodeID!=null) {
			
			// ... und kein Name eingegeben wurde, ...
			if(treeInstProjects.get_text(creatingNodeID)==="") {
				// ... wird der Erstellungs-Vorgang abgebrochen
				treeInstProjects.delete_node(creatingNodeID);
				creatingNodeID = null;
				updateMenuButtonsProject();
			}
			// ... und ein Name eingegeben wurde, ...
			else
				// ... wird severseitig ein neues Projekt mit dem festgelegten Namen erzeugt
				createProject(treeInstProjects.get_text(creatingNodeID));
			}
		// wenn die Eingabe des Names eines zu duplizierenden Projektes bestätigt wurde (= Duplizieren eines Projektes), ...
		else if(duplicateID!=null) {
		
			// ... und kein Name eingegeben wurde, ...
			if(treeInstProjects.get_text(duplicateNodeID)==="") {
				// ... wird der Duplizierungs-Vorgang abgebrochen
				treeInstProjects.delete_node(duplicateNodeID);
				duplicateNodeID = null;
				duplicateID = null;
				updateMenuButtonsProject();
			}
			// ... und ein Name eingegeben wurde, ...
			else
				// ... wird serverseitig das zum duplizieren ausgewählte Projekt mit dem festgelegten Namen dupliziert
				duplicateProject(duplicateID,treeInstProjects.get_text(duplicateNodeID));
		}
		// wenn der neue Name für ein bestehendes Projekt bestätigt wurde (= Umbenennen)
		else if(renameID!=null) {
			
			// ... und kein oder derselbe Name eingegeben wurde, ...
			if(treeInstProjects.get_text(renameID)==="" || treeInstProjects.get_text(renameID)===prevName) {
				// ... wird der Umbenennungs-Vorgang abgebrochen
				//treeInstProjects.set_text(renameID,prevName);
				node = treeInstProjects.get_node(renameID);
				treeInstProjects.set_text(node,getHTML(node));
				renameID = null;
				updateMenuButtonsProject();
			}
			// ... und ein, vom bisherigen Namen verschiedener, Name eingegeben wurde, ...
			else
				// ... wird das serverseitige Umbenennen des betroffenen Projektes eingeleitet
				renameProject(treeInstProjects.get_text(renameID));
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
		creatingNodeID = addNode('project',null);
		// selektiert die erzeugte Knoten-Komponente
		selectNode(creatingNodeID);
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		editNode(creatingNodeID,"");
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen (vollständige Deaktivierung)
		updateMenuButtonsProject();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird createProject() zum serverseitigen Erstellen eines entsprechenden Projektes aufgerufen
	});
	
	// 'Löschen'-Schaltfläche
	$('.projecttoolbar-delete').on("click", function() {
		
		deletingNodeID = selectedNodeIDProjects;
		
	});
	
	// 'Umbenennen'-Schaltfläche
	$('.projecttoolbar-rename').on("click", function() {
		
		node = treeInstProjects.get_node(selectedNodeIDProjects);
		// Projekt-ID des umzubenennenden Projektes
		renameID = node.id;
		// derzeitiger Name des Projektes (für etwaiges Zurückbenennen)
		prevName = node.projectname;
		
		// versetzt die Knoten-Komponente in den Bearbeitungsmodus
		editNode(renameID,node.projectname);
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtonsProject();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird renameProject() zum serverseitigen Umbenennen des betroffenen Projektes aufgerufen
		
	});
	
	// 'Duplizieren'-Schaltfläche
	$('.projecttoolbar-duplicate').on("click", function() {
		
		// Projekt-ID des zu duplizierenden Projektes
		duplicateID = selectedNodeIDProjects;
		
		// erzeugt eine neue Knoten-Komponente
		duplicateNodeID = addNode('project',null);
		// selektiert die erzeugte Knoten-Komponente
		selectNode(duplicateNodeID);
		// versetzt die erzeugte leere Knoten-Komponente in den Bearbeitungsmodus
		editNode(duplicateNodeID,"");
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen (vollständige Deaktivierung)
		updateMenuButtonsProject();
		
		// sobald der Bearbeitungsmodus beendet (s. Umbenennungs-Listener) wird,
		// wird duplicateProject() zum serverseitigen Duplizieren eines entsprechenden Projektes aufgerufen		
		
	});
	
	// 'in Vorlage umwandeln'-Schaltfläche
	$('.projecttoolbar-converttotemplate').on("click", function() {
	
		// Projekt-ID des umzuwandelnden Projektes
		templatizedID = selectedNodeIDProjects;
		
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
	// 'Freigabe entziehen'-Schaltfläche
	$('.projecttoolbar-deny').on("click", function() {
		showInvitedUser();
		
	});
	
	// 'Einladung akzeptieren'-Schaltfläche
	$('.modal_acceptInvitationConfirmation_yes').on("click", function() {
		acceptInvitation();
	});
	// 'Einladung ablehnen'-Schaltfläche
	$('.modal_denyInvitationConfirmation_yes').on("click", function() {
		denyInvitation();
	});

	refreshProjects();
	listInvitations();
});

// ----------------------------------------------------------------------------------------------------
//                                           FUNKTIONALITÄTEN                                          
//                                      (client- und serverseitig)                                     
// ----------------------------------------------------------------------------------------------------

/*
 * Öffnet das momentan ausgewählte Projekt durch Wechseln zu dessen Datei-Übersicht.
 */
function openProject() {
	
	document.location.assign('/dateien/#' + treeInstProjects.get_node(prevSelectedNodeID).rootid);
	
}

/*
 * Der Nutzer akzeptiert die Einladung zum Projekt und nimmt an der Kollabaration teil.
 * @param projectId - Die Id des Projektes, dessen Einladung vom Nutzer akzeptiert wurde.
 */
function acceptInvitation() {
	documentsJsonRequest({
			'command': 'activatecollaboration',
			'id':selectedNodeIDInvitations
		}, function(result,data) {
			if(result) {
				refreshProjects();
				listInvitations();
				showAlertDialog("Einladung zur Kollaboration annehmen","Sie haben die Einladung zur Kollaboration angenommen.");
			}
			else {
				showAlertDialog("Einladung zur Kollaboration annehmen",data.response);
			}
	});
}

/*
 * Der Nutzer lehnt die Einladung zum Projekt zur Kollaboration ab.
 * @param projectId - Die Id des Projektes, dessen Einladung vom Nutzer abgelehnt wurde.
 */
function denyInvitation() {
	documentsJsonRequest({
			'command': 'quitcollaboration',
			'id':selectedNodeIDInvitations
		}, function(result,data) {
			if(result) {
				refreshProjects();
				listInvitations();
				showAlertDialog("Einladung zur Kollaboration ablehnen","Sie haben die Einladung zur Kollaboration abgelehnt.");
			}
			else {
				showAlertDialog("Einladung zur Kollaboration ablehnen",data.response);
			}
	});
}

/*
 * Der Nutzer beendet die Kollaboration.
 * @param projectId - Die Id des Projektes, dessen Einladung vom Nutzer abgelehnt wurde.
 */
function quitCollaboration() {
	documentsJsonRequest({
			'command': 'quitcollaboration',
			'id':selectedNodeIDProjects
		}, function(result,data) {
			if(result) {
				refreshProjects();
				showAlertDialog("Kollaboration beenden","Sie haben die Kollaboration beendet.");
			}
			else {
				showAlertDialog("Kollaboration beenden",data.response);
			}
	});
	
}


/*
 * Sendet an den Account mit der übergebenen E-Mail Adresse eines Nutzers eine Einladung zum Projekt.
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
				showAlertDialog("Projekt freigeben","Der Nutzer wurde zur Kollaboration Ihres Projektes eingeladen.");
				$('.projecttoolbar-deny').prop("disabled", false);

			}
			else {
				showAlertDialog("Projekt freigeben",data.response);
			}
	});
}

/*
 * Entzieht einem Nutzer für ein angegebenes Projekt die Rechte.
 * @param projectId - Die Id des Projektes, von dem für den Nutzer die Rechte entzogen werden.
 * @param user - Der Nutzer, dem die Rechte entzogen werden.
 */
function denyProjectAccess(projectId,user) {
	documentsJsonRequest({
			'command': 'cancelcollaboration',
			'name': user,
			'id':projectId
		}, function(result,data) {
			if(result) {
				showAlertDialog("Freigabe entziehen","Sie haben dem Benutzer erfolgreich die Projektfreigabe entzogen.")
			}
			else {
				showAlertDialog("Freigabe entziehen",data.response);
			}
				updateMenuButtonsProject();
	});
}

/*
 * Gibt die Anzahl der Kollaborationsteilnehmer zurück. 
 * @param projectId - ID des Projektes, das freigegeben wurde.
 */
function getNumberOfInvitedUser(){
	if (selectedNodeIDProjects != ""){
	documentsJsonRequest({
			'command': 'listinvitedusers',
			'id':selectedNodeIDProjects
		}, function(result,data) {
			if(result) {
				number_of_invitedusers = data.response.length;
				if (number_of_invitedusers == 0){
					$('.projecttoolbar-deny').prop("disabled", true);
				}
			}
			else {
			}
	});
	}
}

/*
 * Zeigt die eingeladenen Benutzer an. 
 * @param projectId - ID des Projektes, das freigegeben wurde.
 */
function showInvitedUser(){
	documentsJsonRequest({
			'command': 'listinvitedusers',
			'id':selectedNodeIDProjects
		}, function(result,data) {
			if(result) {
				var number_of_invitedusers = data.response.length;
				document.getElementById('invitedUser').innerHTML = "";
				for (var i = 0; i < number_of_invitedusers; i++){
					document.getElementById('invitedUser').innerHTML = document.getElementById('invitedUser').innerHTML+"<div class=\"row\"><div class=\"col-lg-6\"><div class=\"input-group\"><span class=\"input-group-addon\"><input name=\"denyProjectAccess\" value=\""+data.response[i]+"\" type=\"checkbox\" aria-label=\"checked\"></span><input type=\"text\" class=\"form-control\" disabled aria-label=\"user\" value=\""+data.response[i]+"\"></div></div></div>";
					
				}
				
			}
			else {
			}
	});
}

/*
 * Aktualisiert die Anzeige der Projekte des Benutzers.
 */
function listInvitations() {
	// leert den JSTrees
	treeInstInvitations.settings.core.data = null;
	treeInstInvitations.refresh();
	
	// aktualisiert den JSTree anhand der bestehenden Projekte
	documentsJsonRequest({
		'command': 'listunconfirmedcollaborativeprojects'
		}, function(result,data) {
			if(result) {
				allprojects=data.response;
				// legt für jedes Projekt eine Knoten-Komponente an
				for(var i=0; i<data.response.length; ++i)
					addNode('invitation',data.response[i]);
			}
	});
	
	// aktualisiert die Aktivierungen der Menü-Schaltflächen
	updateMenuButtonsInvitation();
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
				showAlertDialog("Projekt erstellen","Sie haben das Projekt erfolgreich erstellt.");
			}
			// wenn ein entsprechendes Projekt nicht angelegt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				node = treeInstProjects.get_node(creatingNodeID);
				treeInstProjects.set_text(node,getHTML(node));
				treeInstProjects.edit(creatingNodeID,"");
				showAlertDialog("Projekt erstellen",data.response);

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
				treeInstProjects.delete_node(selectedNodeIDProjects);
				
				// setzt die Löschung-ID zurück
				deletingNodeID = null;
				// setzt die Selektions-ID zurück
				selectedNodeIDProjects = "";
				
				// aktualisiert die Aktivierungen der Menü-Schaltflächen
				updateMenuButtonsProject();
				refreshProjects();	
				showAlertDialog("Projekt löschen","Sie haben das Projekt erfolgreich gelöscht");

			}
			else {
				showAlertDialog("Projekt löschen",data.response);
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
				showAlertDialog("Projekt umbenennen","Sie haben das Projekt erfolgreich umbenannt.");
			}
			// wenn das ausgewählte Projekt für den übergebenen Namen nicht umbenannt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				treeInstProjects.edit(renameID,"");
				
				// TEMP
					showAlertDialog("Projekt umbenennen",data.response);
				//showPopover(treeInstProjects.get_node(renameID),data.response);
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
				showAlertDialog("Projekt duplizieren","Sie haben das Projekt erfolgreich dupliziert.");
			}
			// wenn ein entsprechendes Projekt nicht angelegt werden konnte, ...
			else {
				// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
				treeInstProjects.edit(duplicateNodeID,"");
				
				// TEMP
					showAlertDialog("Projekt duplizieren",data.response);
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
				document.getElementById('modal_alertDialog').style.display = 'none';
				// Weiterleitung zu Vorlagen
				document.location.assign('/vorlagen/');
				//showAlertDialog("Projekt in Vorlage umwandeln","Sie haben das Projekt erfolgreich in eine Vorlage umgewandelt.");
			}
			// wenn eine entsprechende Vorlage nicht angelegt werden konnte, ...
			else {
				// TEMP
				showAlertDialog("Projekt in Vorlage umwandeln",data.response);
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
        'id' : treeInstProjects.get_node(prevSelectedNodeID).rootid,

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
				showAlertDialog("Vorlage in Projekt umwandeln","Sie haben die Vorlage erfolgreich in ein Projekt umgewandelt.");
			} else {
				showAlertDialog("Vorlage in Projekt umwandeln",data.response);
            }
	});
}

/*
 * Fügt eine neue Knoten-Komponente anhand des übergebenen Projektes hinzu.
 * 
 * @param project Projekt, anhand dessen Daten eine neue Knoten-Komponente hinzugefügt werden soll
 * @param type - Einladung oder Projekt
 * @return die ID der erzeugten Knoten-Komponente
 */
function addNode(type,project) {
	
	// fügt eine neue Knoten-Komponente hinzu und füllt die Attribute der Knoten-Komponente mit den Werten des übergebenen Projektes
	if (type == 'project'){
	return fillNode(type,treeInstProjects.create_node("#",""),project);
	}
	if (type == 'invitation'){
		return fillNode(type,treeInstInvitations.create_node("#",""),project);
	}
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
	showPopover(treeInstProjects.get_node(nodeID));
	// versetzt die betroffene Knoten-Komponente in den Bearbeitungsmodus
	treeInstProjects.edit(nodeID,text);
}

/*
 * Füllt die Attribute der übergebenen Knoten-Komponente mit den Werten des angegebenen Projektes.
 * 
 * @param nodeID ID der Knoten-Komponente, deren Attribute gemäß des angegebenen Projektes gesetzt werden sollen
 * @param project Projekt, anhand dessen Daten die Attribute der übergebenen Knoten-Komponente gesetzt werden sollen
 *
 * @return die ID der Knoten-Komponente
 */
function fillNode(type, nodeID,project) {
	if (type == 'project'){
	node = treeInstProjects.get_node(nodeID);
	
	if(project!=null) {
		
		// setzt die ID der Knoten-Komponente auf die des übergebenen Projektes
		treeInstProjects.set_id(node,project.id);
		
		// setzt die weiteren Attribute des Projektes
		node.projectname 		= project.name;
		node.author 			= project.ownername;
		node.createtime 		= project.createtime;
		node.rootid 			= project.rootid;
		
	}
	
	// setzt die Bezeichnung der Knoten-Komponente anhand der Daten des übergebenen Projektes
	treeInstProjects.set_text(node,getHTML(node));
	
	return node.id;
	}
	if (type == 'invitation'){
		node = treeInstInvitations.get_node(nodeID);
	
	if(project!=null) {
		
		// setzt die ID der Knoten-Komponente auf die des übergebenen Projektes
		treeInstInvitations.set_id(node,project.id);
		
		// setzt die weiteren Attribute des Projektes
		node.projectname 		= project.name;
		node.author 			= project.ownername;
		node.createtime 		= project.createtime;
		node.rootid 			= project.rootid;
		
	}
	
	// setzt die Bezeichnung der Knoten-Komponente anhand der Daten des übergebenen Projektes
	treeInstInvitations.set_text(node,getHTML(node));
	
	return node.id;
	}
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
	treeInstProjects.settings.core.data = null;
	treeInstProjects.refresh();
	
	// aktualisiert den JSTree anhand der bestehenden Projekte
	documentsJsonRequest({
		'command': isProjectsPage ? 'listprojects' : 'listtemplates',
		}, function(result,data) {
			if(result) {
				allprojects=data.response;
				// legt für jedes Projekt eine Knoten-Komponente an
				for(var i=0; i<data.response.length; ++i)
					addNode('project',data.response[i]);
			}
	});
	
	// aktualisiert die Aktivierungen der Menü-Schaltflächen
	updateMenuButtonsProject();
}

/*
 * Selektiert die, der übergebenen ID entsprechende, Knoten-Komponente.
 * Hierbei wird die momentan ausgewählte Knoten-Komponente deselektiert.
 *
 * @param nodeID ID der Knoten-Komponente, welche selektiert werden soll
 */
function selectNode(nodeID) {
	
	treeInstProjects.deselect_node(treeInstProjects.get_selected());
	treeInstProjects.select_node(nodeID);
	selectedNodeIDProjects = nodeID;
	
	selectedPos 	= $('.node_item_'+selectedNodeIDProjects).position();
	selectedHeight 	= $('.node_item_'+selectedNodeIDProjects).height();
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
 * Aktualisiert die Aktivierungen der Menü-Schaltflächen des Projektes.
 */
function updateMenuButtonsProject() {
	
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
	else if(treeInstProjects.get_selected().length!=0) {
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
	$('.projecttoolbar-quitCollaboration').prop("disabled", !remain);
	getNumberOfInvitedUser();
	if (currentAuthor == user){
		$('.projecttoolbar-quitCollaboration').prop("disabled", true);
	}
	else {
		$('.projecttoolbar-share').prop("disabled", true);
		$('.projecttoolbar-deny').prop("disabled", true);
		$('.projecttoolbar-quitCollaboration').prop("disabled", false);
		$('.projecttoolbar-delete').prop("disabled", true);
		$('.projecttoolbar-rename').prop("disabled", true);
		$('.projecttoolbar-duplicate').prop("disabled", true);
	//	$('.projecttoolbar-converttotemplate').prop("disabled", true);

	}
	$('.templatestoolbar-use').prop("disabled", !remain);
}

/*
 * Setzt den Inhalt des Alert Dialogs.
 */
function showAlertDialog(title,message){
		$('#modal_alertDialog').modal('show');
		document.getElementById('modal_alertDialog_title').innerHTML = title;
		document.getElementById('modal_alertDialog_message').innerHTML = message;
}

/*
 * Entfernt die alten Nachrichten aus dem Alert Dialog.
 */
function clearAlertDialog(){
		showAlertDialog("","");
}


/*
 * Aktualisiert die Aktivierungen der Menü-Schaltflächen der Einladung.
 */
function updateMenuButtonsInvitation() {
	
	// flag für die Aktivierung der selektionsabhängigen Schaltflächen
	var remain;
	
	// Selektion
	if(treeInstInvitations.get_selected().length!=0) {
		// vollständig Aktivierung
		basic  = true;
		remain = true;
	}
	
	
	// setzt die Aktivierungen der einzelnen Menü-Schaltflächen
	$('.invitationtoolbar-acceptInvitation').prop("disabled", !remain);
	$('.invitationtoolbar-denyInvitation').prop("disabled", !remain);
}
	
