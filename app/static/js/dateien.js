/*
@author: Timo Dümke
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 12.12.2014 - sprint-nr: 3
*/
var filelistHandler;
$( document ).ready(function() {
// ID aus URL ermitteln
	id = parseInt(location.hash.substr(1));
	if (isNaN(id)){
		backToProject();
		}
	else {
filelistHandler = new ListSelector("dateien");
filelistHandler.setCaptions([
{'name': 'Ordner', 'element': 'foldername'},
{'name': 'Name', 'element': 'name'},
{'name': 'Dateityp', 'element': 'filetype'}
]);
//filelistHandler.addData({'name': 'TestProjekt2', 'foldername': 'bla'});

//filelistHandler.addData(filelistHandler.addData({'name': 'File1', 'foldername': 'Administrator'},[0]));
//filelistHandler.addData({'name': 'File 2', 'foldername': 'Administrator'},[0,0]);
//	filelistHandler.addData({'name': 'TroProjekt 2', 'foldername': 'Administrator'},[0,0,0]);

	//filelistHandler.addData({'name': 'Demo-Projekt', 'foldername': 'TestBenutzer'}, [0],false);
	//filelistHandler.addData({'name': 'TestProjekt2', 'foldername': 'AndererBenutzer'});

	showFilelist(id);
}
});

function showFilelist(projectID){
//alert(projectID);
jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'listfiles',
			'id': projectID
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			//Anfrage Fehlerhaft
			console.log({
				'error': 'Fehlerhafte Anfrage: Fehler beim Abrufen der Dateiliste',
				'details': errorThrown,
				'id': projectID,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success'){
				// Fehler auf dem Server
				console.log({
					'error': 'Fehlerhafte Rückmeldung: Fehler beim Abrufen der Dateiliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			}
			else {
			// vorhandene Dateiliste entfernen
			filelistHandler.clearData();
			//console.log(data.response);
			/**var files = data.response.files;
			console.log(data.response);
			console.log(data.response.folders);
			// Gehe eine Stufe tiefer
			
			**/
			analyseFolders(data.response,0,'0',null,false);
			
			
		}
		}
	});
}

function analyseFolders(response,level,path,parent,leaf){
//path = "["+path+"]";
var number_of_files = response.files.length;


if (level == 0){
for (var i = 0; i < response.files.length; i++){
	filelistHandler.addData({'name':response.files[i].name,'foldername':response.name});
}
}
else {
for (var i = 0; i < response.files.length; i++){
//console.log(response);
	filelistHandler.addData({'name':response.files[i].name,'foldername':response.name},path,false);
	
}
}
if (response.folders.length != 0){
//console.log(" Unterordner");
for (var a=0;a < response.folders.length; a++){
if (level >  0){

if (response.folders[a].folders.length != 0){ // Es gibt unterordner
//alert("Bla");
//console.log("Pfad"+path);
var sumOfFiles = 0;

for (var c=0;c<parent.folders.length;c++){
if (parent.folders[c] === response){
break;
}
sumOfFiles += parent.folders[c].files.length;
}

if (sumOfFiles == 0){
if (response.folders[a].files.length != 0){
//alert("Eltern"+parent.files.length);
sumOfFiles =parent.files.length;
}
}
//alert("SUmme"+(sumOfFiles-response.folders[a].files.length));
path.push(sumOfFiles);
console.log({"Namevorher":(response.folders[a].name),"Path":''+path});

analyseFolders(response.folders[a],level+1,path,response,false);
}
else {
//console.log("Keine Unterordner");
var sumOfFiles = 0;

for (var c=0;c<parent.folders.length;c++){
if (parent.folders[c] === response){
break;
}
sumOfFiles += parent.folders[c].files.length;
}
if (response.files.length > 1){
sumOfFiles += response.files.length-1;
}
//alert("Files"+sumOfFiles);
path.push(sumOfFiles);
console.log({'Name':response.folders[a].name,'Pfad':''+path.toString()});

for (var i = 0; i < response.folders[a].files.length; i++){
	filelistHandler.addData({'name':response.folders[a].files[i].name,'foldername':response.folders[a].name},path,false);
}
//analyseFolders(response,level+1,[path,(parent.files.length-1)],parent,true);


}
}
else {
//console.log("Response:"+response);

analyseFolders(response.folders[a],level+1,[(number_of_files-1)],response,false);


}
}
}



}

function getPath(number){
var path = "[";
for (var c=0;c<number;c++){
if (c> 0){
path += ",";
}
path += "0";
}
path += "]";
return path;
}



function recursiveFolder(folderarray, data, response,level){

console.log('Folderarray'+folderarray.length);
var files = data.response.files;
alert (level);
if (folderarray.length == 0){
if (level == 0){
for (var i = 0; i < files.length; ++i){
			if (i < files.length - 1){
			console.log("Debug1"+data.response.name+"/"+files[i]);
				filelistHandler.addData(files[i],getPath(level), false);
			}
			else{
			console.log("Debug2"+data.response.name+"/"+files[i]);
				filelistHandler.addData(files[i],getPath(level), false);
				}
			}
}

}
else {
if (level == 0){
for (var i = 0; i < files.length; ++i){
			if (i < files.length - 1){
			console.log("Debug1"+data.response.name+"/"+files[i]);
				filelistHandler.addData({'name':files[i].name, 'foldername': data.response.name });
			}
			else{
			console.log("Debug2"+data.response.name+"/"+files[i]);
				filelistHandler.addData({'name':files[i].name, 'foldername': data.response.name });
				}
}
}
for (var i = 0; i < folderarray.length; ++i){
			if (i < files.length - 1){
			console.log("SecondDebug1"+data.response.name+"/"+files[i]);
				filelistHandler.addData({'name':folderarray[i].files.name, 'foldername': folderarray[i].name },getPath(level),false);
				//filelistHandler.addData(files[i], [], false);
				
			}
			else{
			
			// Iterate 
			for (var a = 0; a < folderarray[i].files.length; ++a){
			if (i < files.length - 1){
			console.log("Debug3"+data.response.name+"/"+files[i]);
			console.log("SecondDebug1"+data.response.name+"/"+files[i]);
			
				filelistHandler.addData({'name':folderarray[i].files[a].name, 'foldername': folderarray[i].name },getPath(level),false);
			//filelistHandler.addData(data.reponse);
				//filelistHandler.addData(files[i]);
			}
			else{
			console.log("Debug4"+data.response.name+"/"+files[i]);
			console.log("SecondDebug2"+data.response.name+"/"+files[i]);
			
				filelistHandler.addData({'name':folderarray[i].files[a].name, 'foldername': folderarray[i].name },getPath(level),false);
			//filelistHandler.addData(data.reponse);
				//filelistHandler.addData(files[i]);
				}
}
			
			
				}
				console.log(getPath(3));
				recursiveFolder(folderarray[i].folders,data,response,level+1);
}



}


}




/**
 * Leitet den Benutzer zurück zur Projektverwaltung.
 */
function backToProject() {
	// TODO: auf das richtige Projekt verweisen?
	window.location.replace('/projekt/');
}

