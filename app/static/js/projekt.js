/*
 * @author: Thore Thießen, Ingolf Bracht, Munzir Mohamed, Kirill Maltsev
 * @creation: 04.12.2014 - sprint-nr: 2
 * @last-change: 03.02.2015 - sprint-nr: 6
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

var selectedNodeIDProjects = "";
var selectedNodeIDInvitations = "";
var prevSelectedNodeID 	= "";
var postSelection = false;			// gibt an, ob eine explizite Nachselektion notwendig ist (bei 'Umbenennen')

var allprojects=null;				// Array von allen Projekten

var treeInstInvitations;
var treeInstProjects;

var isProjectsPage = true;			// false für die Seite mit Vorlagen;

var sorting = 0;					// Sortierungsvariable ( 0 = Name, 1 = Erstellungsdatum, 2 = Autor )
var sortOrder = 1;					// Sortierungsrichtung ( 1 = aufsteigend, -1 = absteigend )
var ignoreSorting = false;			// für temporäres Ignorieren der Sortierung bei anlegender Knoten-Komponente ('Erstellen' und 'Duplizieren')
var sortReplacements = {"ä":"a", "ö":"o", "ü":"u", "ß":"ss" };

/*
 * Initialisiert den JSTree und die Menü-Einträge.
 */
$(function() {
	
	isProjectsPage = $(".templateswrapper").length === 0;
	
	refreshProjects();
	if(isProjectsPage)
		refreshInvitations();
	
	
	// Modal zum Bestätigen/Abbrechen des Löschvorgangs
	$('#modal_deleteConfirmation').on('hidden.bs.modal', function(e) {
		// fokussiert den JSTree, um nach Abbruch des Löschvorgangs Tasten-Events behandeln zu können
		//treeProjects.focus();
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
		sendProjectInvitation(selectedNodeIDProjects, $('#modal_shareuser_tf').val());
        $('#modal_shareuser_tf').val("");
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
			var owner=allprojects[i].ownername;
			if (proj==filename && owner==user){
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
	
	initSorting();
	
	
	// ----------------------------------------------------------------------------------------------------
	//                                             MENÜ-EINTRÄGE                                           
	// ----------------------------------------------------------------------------------------------------

	// 'Kollaboration'-Dropdown
	$('.projecttoolbar-collabo').on("click", function() {
	    // mach gar nichts
	});

	// 'Öffnen'-Schaltfläche
	$('.projecttoolbar-open').on("click", function() {
		
		openProject();
		
	});
	
	// 'Erstellen'-Schaltfläche
	$('.projecttoolbar-new').on("click", function() {
		
		// erzeugt eine neue Knoten-Komponente
		ignoreSorting = true;
		creatingNodeID = treeInstProjects.create_node("#","");
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
		prevName = ""+treeInstProjects.get_node(renameID).li_attr["data-name"];
		
		// versetzt die Knoten-Komponente in den Bearbeitungsmodus
		editNode(renameID,prevName);
		
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
		ignoreSorting = true;
		duplicateNodeID = treeInstProjects.create_node("#","");
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
		node = treeInstProjects.get_node(selectedNodeIDProjects);
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
	
	
	
	// ----------------------------------------------------------------------------------------------------
	//                                                JSTREE                                               
	//                                               PROJEKTE                                              
	// ----------------------------------------------------------------------------------------------------
	
	/*
	 * Aktualisiert die Anzeige der Projekte des Benutzers.
	 */
	function refreshProjects() {
		
		// aktualisiert den JSTree anhand der bestehenden Projekte
		documentsJsonRequest({
			'command': isProjectsPage ? 'listprojects' : 'listtemplates',
			}, function(result,data) {
				if(result) {
					allprojects=data.response;
					renderProjects(data.response);
				}
		});
		
		// aktualisiert die Aktivierungen der Menü-Schaltflächen
		updateMenuButtonsProject();
	}
	
    var treeProjects = null;
    function renderProjects(data) {
    	
        var jsTreeProjectsData = transcodeProjectsData(data);

        if(treeProjects) {
            treeInstProjects.settings.core.data = jsTreeProjectsData;
            ignoreSorting = false;
            treeInstProjects.refresh();
            return;
        }
        
		treeProjects = $('.projectswrapper').jstree({
			core: {
				check_callback: true,
				multiple: false,
				data: jsTreeProjectsData
			},
            plugins: ["sort","state"],
            sort: function(a,b) {
            	
            	if(ignoreSorting)
            		return -1;
            	
            	var compare = 1;
            	
            	// Sortierung nach Projektname (auch bei Sortierung nach Autor für zwei Knoten-Komponenten mit demselben Autor)
            	if(sorting==0 || (sorting==2 && this.get_node(a).li_attr["data-author"]==this.get_node(b).li_attr["data-author"]))
            		compare = (""+this.get_node(a).li_attr["data-name"]).toLowerCase().replace(/[äöüß]/g, function($0) { return sortReplacements[$0] }) >
            				  (""+this.get_node(b).li_attr["data-name"]).toLowerCase().replace(/[äöüß]/g, function($0) { return sortReplacements[$0] }) ? 1 : -1;
            	// Sortierung nach Erstellungsdatum
            	else if(sorting==1)
            		compare = this.get_node(a).li_attr["data-createtime"] < this.get_node(b).li_attr["data-createtime"] ? 1 : -1;
            	// Sortierung nach Autor (bei übereinstimmenden Autoren erfolgt Sortierung nach Projektname s.o.)
            	else if(sorting==2)
            		compare = this.get_node(a).li_attr["data-author"] > this.get_node(b).li_attr["data-author"] ? 1 : -1;
            	
            	return compare*sortOrder;
			}
        });
        
        treeInstProjects = $('.projectswrapper').jstree();
        
		// ----------------------------------------------------------------------------------------------------
		//                                               LISTENER                                              
		// ----------------------------------------------------------------------------------------------------
		
		// Refresh-Listener (für Nachselektion, notwendig beim 'Umbenennen')
		treeProjects.bind('refresh.jstree',function(e) {
			
			if(postSelection) {
				
				// stellt den Zustand des JSTrees (zusätzlich) wieder her
				// (es erfolgt keine zusätzliche Zustandsspeicherung)
				treeInstProjects.restore_state();
				
				postSelection = false;
			}
			
		});
		
		// ----------------------------------------------------------------------------------------------------
		
		// Erzeugungs-Listener (für Auto-Selektion)
		treeProjects.bind('create_node.jstree',function(e,data) {
			
			// selektiert die erzeugte Knoten-Komponente
			selectNode(data.node);
			
		});
		
		// ----------------------------------------------------------------------------------------------------
		
		// Auswahl-Listener
		treeProjects.bind('select_node.jstree',function(e,data) {
			
			// Deselektion (die der Selection-ID zugehörige Knoten-Komponente wurde erneut selektiert)
			if(selectedNodeIDProjects===data.node.id) {
				
				// deselektiert die betroffene Knoten-Komponente
				treeInstProjects.deselect_node(data.node.id);
				// setzt die Selection-ID zurück
				selectedNodeIDProjects = "";
				
				// setzt den Autor zurück
				currentAuthor = user;
				
			}
			// Selektion (eine Knoten-Komponente wurde selektiert, deren ID nicht mit der Selection-ID übereinstimmt)
			else {
				
				// aktualisiert die Selection-ID gemäß der ausgewählten Knoten-Komponente
				selectedNodeIDProjects = data.node.id;
				currentAuthor = data.node.li_attr["data-author"];
				prevSelectedNodeID = data.node.id;
				
			}
			
			// aktualisiert die Aktivierungen der Menü-Schaltflächen
			updateMenuButtonsProject();
		});
		
		// ----------------------------------------------------------------------------------------------------
		
		// Doppelklick-Listener
		treeProjects.bind("dblclick.jstree",function(e) {
			
			openProject();
			
		});
		
		// ----------------------------------------------------------------------------------------------------
		
		// Tasten-Listener
		treeProjects.bind('keydown',function(e) {
			
			// Entf-Taste
			if(e.keyCode===46 && !editMode) {
				deletingNodeID = selectedNodeIDProjects;
				$('#modal_deleteConfirmation').modal('show');
			}
			
		});
		
		// ----------------------------------------------------------------------------------------------------
		
		// Umbenennungs-Listener (für 'Erstellen', 'Umbenennen' und 'Duplizieren')
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
				
				// indiziert explizite Nachselektion (s. Refresh-Listener)
				postSelection = true;
				
				// ... und kein oder derselbe Name eingegeben wurde, ...
				if(treeInstProjects.get_text(renameID)==="" || treeInstProjects.get_text(renameID).toLowerCase()===prevName.toLowerCase()) {
					// ... wird der Umbenennungs-Vorgang abgebrochen
					renameID = null;
					refreshProjects();
				}
				// ... und ein, vom bisherigen Namen verschiedener, Name eingegeben wurde, ...
				else
					// ... wird das serverseitige Umbenennen des betroffenen Projektes eingeleitet
					renameProject(treeInstProjects.get_text(renameID));
			}
			
		});
	}
	
	// ----------------------------------------------------------------------------------------------------
	
    var projectTemplate = doT.template($("#template_projectsitem").text());
	
	function transcodeProjectsData(rawData) {
		
        var jsTreeProjectsData = [];
        
        $.each(rawData || [], function (i,project) {
        	
        	project.createTime = getRelativeTime(project.createtime);
        	
            jsTreeProjectsData.push({
                id: project.id,
                text: projectTemplate(project),
                li_attr: {"class": "projectsitem", "data-id": project.id,
                								   "data-name": project.name,
                								   "data-createtime": project.createtime,
                								   "data-author": project.ownername,
                								   "data-rootid": project.rootid}
            });
        });

        return jsTreeProjectsData;
    }
	
	// ----------------------------------------------------------------------------------------------------
	//                                               JSTREE                                                
	//                                             EINLADUNGEN                                             
	// ----------------------------------------------------------------------------------------------------
	
	/*
	 * Aktualisiert die Anzeige der Einladungen des Benutzers.
	 */
	function refreshInvitations() {
		
		// Einladungen-Bereich wird versteckt
		// (wieder sichtbar gesetzt unter updateMenuButtonsInvitation(), sofern Einladungen vorliegen)
		$('#invitations').hide();
		
		// aktualisiert den JSTree anhand der bestehenden Einladungen
		documentsJsonRequest({
			'command': 'listunconfirmedcollaborativeprojects',
			}, function(result,data) {
				if(result) {
					
					renderInvitations(data.response);
					
					// wenn Einladungen vorliegen
					if(data.response.length!=0)
						updateMenuButtonsInvitation();
				}
		});
	}
	
    var treeInvitations = null;
    function renderInvitations(data) {
    	
        var jsTreeInvitationsData = transcodeInvitationsData(data);

        if(treeInvitations) {
            treeInstInvitations.settings.core.data = jsTreeInvitationsData;
            treeInstInvitations.refresh();
            return;
        }
        
		treeInvitations = $('.invitationswrapper').jstree({
			core: {
				check_callback: true,
				multiple: false,
				data: jsTreeInvitationsData
			},
			plugins: ["state"]
		});
        
        treeInstInvitations = $('.invitationswrapper').jstree();
        
		// ----------------------------------------------------------------------------------------------------
		//                                               LISTENER                                              
		// ----------------------------------------------------------------------------------------------------
		
		// Auswahl-Listener
		treeInvitations.bind('select_node.jstree',function(e,data) {
			
			// Deselektion (die der Selection-ID zugehörige Knoten-Komponente wurde erneut selektiert)
			if(selectedNodeIDInvitations===data.node.id) {
				
				// deselektiert die betroffene Knoten-Komponente
				treeInstInvitations.deselect_node(data.node.id);
				// setzt die Selection-ID zurück
				selectedNodeIDInvitations = "";
				
			}
			// Selektion (eine Knoten-Komponente werde selektiert, deren ID nicht mit der Selection-ID übereinstimmt)
			else {
				
				// aktualisiert die Selection-ID gemäß der ausgewählten Knoten-Komponente
				selectedNodeIDInvitations = data.node.id;
				
			}
			
			// aktualisiert die Aktivierungen der Menü-Schaltflächen
			updateMenuButtonsInvitation();
		});
	
	}
	
	// ----------------------------------------------------------------------------------------------------
	
	function transcodeInvitationsData(rawData) {
		
        var jsTreeInvitationsData = [];
        
        $.each(rawData || [], function (i,invitation) {
        	
        	invitation.createTime = getRelativeTime(invitation.createtime);
        	
            jsTreeInvitationsData.push({
                id: invitation.id,
                text: projectTemplate(invitation),
                li_attr: {"class": "invitationsitem", "data-id": invitation.id,
                									  "data-name": invitation.name,
                									  "data-author": invitation.ownername,
                									  "data-rootid": invitation.rootid}
            });
        });
        
        return jsTreeInvitationsData;
    }
    
    
    
	// ----------------------------------------------------------------------------------------------------
	//                                           FUNKTIONALITÄTEN                                          
	//                                      (client- und serverseitig)                                     
	// ----------------------------------------------------------------------------------------------------
	
	/*
	 * Öffnet das momentan ausgewählte Projekt durch Wechseln zu dessen Datei-Übersicht.
	 */
	function openProject() {
		
		document.location.assign('/dateien/#' + treeInstProjects.get_node(prevSelectedNodeID).li_attr["data-rootid"]);
		
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
						
						treeInstProjects.set_id(treeInstProjects.get_node(creatingNodeID),data.response.id);
						
						if(name!=data.response.name)
							showAlertDialog("Projekt erstellen",
											"Ein Projekt mit dem Namen "+name+" existiert bereits:<br>"+
											"Es wurde ein neues Projekt <b>"+data.response.name+"</b> erstellt.");
						}
					// wenn ein entsprechendes Projekt nicht angelegt werden konnte, ...
					else {
						// ... wird die Knoten-Komponente zur Angabe eines neuen Namens erneut in den Bearbeitungsmodus versetzt (s. Umbenennungs-Listener)
						// node = treeInstProjects.get_node(creatingNodeID);
						// treeInstProjects.set_text(node,getHTML(node));
						// treeInstProjects.edit(creatingNodeID,"");
						showAlertDialog("Projekt erstellen",data.response);
					}
					
					// setzt die Erstellungs-ID zurück
					creatingNodeID = null;
					
					// aktualisiert die Anzeige der Projekte
					refreshProjects();
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
				if(result) {
					
					// entfernt die zugehörige Knoten-Komponente
					treeInstProjects.delete_node(deletingNodeID);
					
					// setzt die Löschung-ID zurück
					deletingNodeID = null;
					// setzt die Selektions-ID zurück
					selectedNodeIDProjects = "";
					
				}
				else
					showAlertDialog((isProjectsPage ? "Projekt" : "Vorlage")+" löschen",data.response);
				
				// aktualisiert die Anzeige der Projekte
				refreshProjects();
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
				
				// wenn das ausgewählte Projekt für den übergebenen Namen nicht umbenannt werden konnte
				if(!result)
					showAlertDialog((isProjectsPage ? "Projekt" : "Vorlage")+" umbenennen",data.response);
				
				// setzt die Umbenennungs-IDs zurück
				renameID = null;
				prevName = null;
				
				// aktualisiert die Anzeige der Projekte
				refreshProjects();
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
					treeInstProjects.set_id(treeInstProjects.get_node(duplicateNodeID),data.response.id);
					if(name!=data.response.name)
						showAlertDialog("Projekt duplizieren",
										"Ein Projekt mit dem Namen "+name+" existiert bereits:<br>"+
										"Es wurde ein neues Projekt <b>"+data.response.name+"</b> erstellt.");
				}
				// wenn ein entsprechendes Projekt nicht angelegt werden konnte, ...
				else
					showAlertDialog("Projekt duplizieren",data.response);
				
				// setzt die Duplizierungs-IDs zurück
				duplicateNodeID = null;
				duplicateID = null;
				
				// aktualisiert die Anzeige der Projekte
				refreshProjects();
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
			
				// setzt die Umwandlungs-ID zurück
				templatizedID = null;
				document.getElementById('modal_alertDialog').style.display = 'none';
				
				// wenn eine entsprechende Vorlage angelegt wurde, ist der Umwandlungs-Vorgang abgeschlossen
				if(result) {
					
					if(name!=data.response.name)
						showAlertDialog("Projekt in Vorlage umwandeln",
						                "Eine Vorlage mit dem Namen "+name+" existiert bereits:<br>"+
									    "Es wurde eine neue Vorlage <b>"+data.response.name+"</b> erstellt.",
									    "/vorlagen/");
					else
						// Weiterleitung zu den Vorlagen
						window.location.replace("/vorlagen/");
				}
				// wenn eine entsprechende Vorlage nicht angelegt werden konnte
				else
					showAlertDialog("Projekt in Vorlage umwandeln",data.response);
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
	        'id' : treeInstProjects.get_node(prevSelectedNodeID).li_attr["data-rootid"],
	
	    }, function(result,data) {
	        if(result) {
	            console.log('Export Done!')
	            }
	        }
	    );
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
					$('.projecttoolbar-deny').toggleClass("disabled", false);
	                refreshProjects();
				} else {
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
					showAlertDialog("Freigabe entziehen","Sie haben den ausgewählten Benutzern erfolgreich die Projektfreigabe entzogen.");
					refreshProjects();
				} else {
					showAlertDialog("Freigabe entziehen",data.response);
				}
				updateMenuButtonsProject();
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
				} else {
					showAlertDialog("Kollaboration beenden",data.response);
				}
		});
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
					refreshInvitations();
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
					refreshInvitations();
					showAlertDialog("Einladung zur Kollaboration ablehnen","Sie haben die Einladung zur Kollaboration abgelehnt.");
				}
				else {
					showAlertDialog("Einladung zur Kollaboration ablehnen",data.response);
				}
		});
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
	        	
				// setzt die Umwandlungs-ID zurück
				projectTempID = null;
	        	
	        	// wenn ein entsprechendes Projekt angelegt wurde, ist der Umwandlungs-Vorgang abgeschlossen
				if(result) {
					
					if(name!=data.response.name)
						showAlertDialog("Vorlage in Projekt umwandeln",
						                "Ein Projekt mit dem Namen "+name+" existiert bereits:<br>"+
									    "Es wurde ein neues Projekt <b>"+data.response.name+"</b> erstellt.",
									    "/projekt/");
					else
						// Weiterleitung zu den Projekten
						window.location.replace("/projekt/");
				} else {
					showAlertDialog("Vorlage in Projekt umwandeln",data.response);
	            }
		});
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
		showPopover(treeInstProjects.get_node(nodeID));
		// versetzt die betroffene Knoten-Komponente in den Bearbeitungsmodus
		treeInstProjects.edit(nodeID,text);
	}
	
	/*
	 * Liefert den aktuellen Cookie-Schlüssel.
	 */
	function getCookieKey(sortValue) {
		return encodeURIComponent(user)+"#"+(isProjectsPage ? "P" : "T");
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
					if(0<=sortingNum && sortingNum<=2)
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
		
		treeInstProjects.deselect_node(treeInstProjects.get_selected());
		if(treeInstProjects.get_node(nodeID)!=null) {
		
			treeInstProjects.select_node(nodeID);
			selectedNodeIDProjects = nodeID;
			currentAuthor = treeInstProjects.get_node(nodeID).author;
			prevSelectedNodeID = nodeID;
		}
		else {
			
			selectedNodeIDProjects = "";
			currentAuthor = user;
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
		});
	}
	
	/*
	 * Zeigt das Popover in relativer Position zur übergebenen Knoten-Komponente an.
	 *
	 * @param node Knoten-Komponente zu deren Position das Popover relativ angezeigt werden soll
	 */
	function showPopover(node) {
		
		if(node!=null && treeInstProjects.get_node(node.id)) {
			
			var popover = $('.input_popover');
			
			// zeigt das Popover an und richtet es links über der Knoten-Komponente aus
			// (Reihenfolge nicht verändern!)
			popover.popover('show');
	        $('.popover').css('left',$("#"+node.id).position().left+'px');
	        $('.popover').css('top',($("#"+node.id).position().top-43)+'px');
		}
	}
	
	/*
	 * Aktualisiert die Aktivierungen der Menü-Schaltflächen des Projektes.
	 */
	function updateMenuButtonsProject() {
		
		/*
		 * flag für die Aktivierung derjenigen Schaltflächen,
		 * deren zugehörige Funktionalitäten KEINER Selektion bedürfen
		 * ('Erstellen' und 'Import')
		 */
		var flag_basic;
		/*
		 * flag für die Aktivierung derjenigen Schaltflächen,
		 * deren zugehörige Funktionalitäten einer Selektion bedürfen UND ausschließlich dem ProjectOwner vorbehalten sind
		 * ('Löschen', 'Umbenennen', 'Freigeben' und 'Freigabe entziehen')
		 */
		var flag_owner;
		/*
		 * flag für die Aktivierung derjenigen Schaltflächen,
		 * deren zugehörige Funktionalitäten einer Selektion bedürfen
		 */
		var flag_remain;
		
		
		// Editierungsmodus
		if(editMode) {
			
			// keine Aktivierungen, solange Editierungsmodus aktiv
			flag_basic  = false;
			flag_owner  = false;
			flag_remain = false;
			
		}
		// Selektion
		else if(treeInstProjects && treeInstProjects.get_selected().length!=0) {
			
			// Aktivierung aller Schaltflächen ohne notwendige ProjectOwner-Rechte
			flag_basic  = true;
			flag_remain = true;
			
			// Aktivierung der Schaltflächen mit notwendigen ProjectOwner-Rechten
			flag_owner  = currentAuthor==user;
			
		}
		// keine Selektion
		else {
			
			// Aktivierung lediglich der nicht-selektionsabhängigen Schaltflächen
			flag_basic  = true;
			flag_remain = false;
			flag_owner  = false;
		}
		
		$('.projecttoolbar-open').prop("disabled", !flag_remain);
		$('.projecttoolbar-new').prop("disabled", !flag_basic);
		$('.projecttoolbar-delete').prop("disabled", !flag_owner);
		$('.projecttoolbar-rename').prop("disabled", !flag_owner);
		$('.projecttoolbar-duplicate').prop("disabled", !flag_remain);
		$('.projecttoolbar-converttotemplate').prop("disabled", !flag_remain);
		$('.projecttoolbar-export').prop("disabled", !flag_remain);
		$('.projecttoolbar-import').prop("disabled", !flag_basic);

		$('.projecttoolbar-collabo').prop("disabled", !flag_remain);

		// .projecttoolbar-share ist kein <button>, deshalb funktioniert prop("disabled") nicht
		$('.projecttoolbar-share').toggleClass("disabled", !flag_owner);
		$('.projecttoolbar-quitCollaboration').toggleClass("disabled", !flag_remain || flag_owner);
		
		/*
		 * Aktualisiert die 'Freigabe entziehen'-Menü-Schaltfläche
		 * in Abhängigkeit dessen, ob für das selektierte Projekt eingeladene Nutzer vorliegen
		 */

		if(isProjectsPage && !editMode && flag_owner) {
			documentsJsonRequest({
					'command': 'hasinvitedusers',
					'id':selectedNodeIDProjects
				},
				function(result,data) {
					if(result) {
						$('.projecttoolbar-deny').toggleClass("disabled", !data.response);
                    }
				});
		} else {
			$('.projecttoolbar-deny').toggleClass("disabled", true);
        }
		
		$('.templatestoolbar-use').prop("disabled", !flag_remain);
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
		
		$('#invitations').show();
		
		// flag für die Aktivierung der selektionsabhängigen Schaltflächen
		var flag_remain;
		
		// Selektion
		if(treeInstInvitations.get_selected().length!=0)
			// vollständig Aktivierung
			flag_remain = true;
		
		// setzt die Aktivierungen der einzelnen Menü-Schaltflächen
		$('.invitationtoolbar-acceptInvitation').prop("disabled", !flag_remain);
		$('.invitationtoolbar-denyInvitation').prop("disabled", !flag_remain);
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
		treeInstProjects.refresh();
		
	}
});