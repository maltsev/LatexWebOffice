var syntax = [
    "Hello",
    "World",
    "Whats"
];
window.onload = function() {
    var editorFrame = document.getElementsByTagName('iframe');
    for (var i = 0, len = editorFrame.length, doc; i < len; ++i) {
        doc = editorFrame[i].contentDocument || editorFrame[i].contentWindow.document;
        doc.designMode = "on";
		 if(doc.addEventListener) {
    	doc.addEventListener("keyup", autoComplete, true)
    }
    else { //For IE
    	doc.attachEvent("onkeyup", autoComplete);
    }
    }
};
var cursorPosition = 0;
var savedRange,isInFocus;

function autoComplete(e){
var startsign = "{";
var endsign = "}";
if (e.ctrlKey && e.altKey && e.keyCode == 55) { // Code for opening bracket
//brackets ++;
var iframeeditor = document.getElementById("editor");

		var iframeBody = (iframeeditor.contentDocument || iframeeditor.contentWindow.document).body;
		var editorcontent =  iframeBody.innerText;
		if (editorcontent == undefined){
			editorcontent = iframeBody.textContent;
		}
		cursorPosition = getCaretCharacterOffsetWithin(iframeBody);
		//alert(getCaretCharacterOffsetWithin(iframeBody));
		var oldvalue = document.getElementById('editor').contentWindow.document.body.innerText;
		if (oldvalue == undefined){
		oldvalue = document.getElementById('editor').contentWindow.document.body.textContent;
		}
		if (oldvalue.charAt((((cursorPosition-1))+1)-2) != "\\"){
		//alert(oldvalue.charAt((((cursorPosition-1))+1)-2));
		oldvalue = oldvalue.replace(/\r|\n/g, ""); // Zeilenumbrüche entfernen
			// Inhalt bis zum Zeichen in einer temporären Variable speichern
			oldvalue_before = oldvalue.slice(0,((oldvalue.indexOf(startsign,cursorPosition-1))+1));
			// Konsolenausgabe zu Debugging Zwecken 
			//console.log("Alt"+oldvalue_before);
			// Inhalt nach zum Zeichen in einer temporären Variable speichern
			oldvalue_after = oldvalue.slice(((oldvalue.indexOf(startsign,cursorPosition-1))+1), oldvalue.length);
			// HTML Tags entfernen
			oldvalue = document.getElementById('editor').contentWindow.document.body.innerText;
			// Sonderfall für Mozilla Firefox
			if (oldvalue != undefined){
			// Inhalt vor dem Zeichen und nach dem Zeichen zusammenfügen und automatisch das gewünschte Zeichen setzen.
			document.getElementById('editor').contentWindow.document.body.innerText = oldvalue_before+endsign+oldvalue_after;
			// Speichern des neuen Inhalts in einer temporären Variable
			oldvalue = document.getElementById('editor').contentWindow.document.body.innerText;
			}
			// Für die anderen Browser
			else {
			// Analog s.o. (nur mit textContent statt innerText)
			document.getElementById('editor').contentWindow.document.body.textContent = oldvalue_before+endsign+oldvalue_after;
			oldvalue = document.getElementById('editor').contentWindow.document.body.textContent;
			}
	
	// Ergänze Zeilenumbrüche nach den Zeichen
	oldvalue = replaceAll(startsign, startsign+"<br><br>",oldvalue);
	oldvalue = replaceAll(endsign, endsign+"<br><br>",oldvalue);
	// Füge den geänderten Text wieder zum Editorfenster hinzu.
	document.getElementById('editor').contentWindow.document.body.innerHTML = oldvalue;
	}
/**
		//if (document.getElementById('editor').contentWindow.document.body.innerText.lastIndexOf("}") > getCaretCharacterOffsetWithin(iframeBody)){
		//		if (editorcontent.lastIndexOf("}") > getCaretCharacterOffsetWithin(iframeBody)){
				if (editorcontent.lastIndexOf("}") > getCaretCharacterOffsetWithin(iframeBody) && editorcontent.indexOf("{")+1 < getCaretCharacterOffsetWithin(iframeBody)){
				alert("Case1");
		
oldvalue = document.getElementById('editor').contentWindow.document.body.innerHTML;
oldvalue = remove_tags(oldvalue);
// breaks 
     var breaks =  oldvalue.slice(0,cursorPosition).match(/<br>/ig).length + 1;
alert("Breaks"+breaks);
		oldvalue_before = oldvalue.slice(0,(cursorPosition+(4*(breaks-1))));
		alert("Position:"+(cursorPosition+(3*breaks)));
	oldvalue_after = oldvalue.slice((cursorPosition+(4*(breaks-1))), oldvalue.length);
		console.log("Before:"+oldvalue_before);
		console.log("After:"+oldvalue_after);
		document.getElementById("editor").contentWindow.document.body.innerHTML = oldvalue_before+"<br><br>\t}<br>"+oldvalue_after;
	oldvalue = document.getElementById('editor').contentWindow.document.body.innerHTML;
	console.log("Added"+oldvalue);
		oldvalue = replaceAll("<div>", "",oldvalue);
oldvalue = replaceAll("</div>", "",oldvalue);
		document.getElementById('editor').contentWindow.document.body.innerHTML  = oldvalue;
			console.log(document.getElementById('editor').contentWindow.document.body.innerHTML );
		}
		else {
		
		
		alert("Case2");
		//document.getElementById("editor").innerHTML = oldvalue+"<br/>\t<br/>}";
		//oldvalue.lastIndexOf("<br/>");
	//	alert(oldvalue);
		// Remove divs
		oldvalue = document.getElementById('editor').contentWindow.document.body.innerText;
		if (oldvalue == undefined){
			oldvalue = document.getElementById('editor').contentWindow.document.body.textContent;
		}
	document.getElementById('editor').contentWindow.document.body.innerHTML = oldvalue+"\t}";
	oldvalue = document.getElementById('editor').contentWindow.document.body.innerHTML;
oldvalue = replaceAll("<div>", "",oldvalue);
oldvalue = replaceAll("</div>", "",oldvalue);
oldvalue = replaceAll("{", "{<br><br>",oldvalue);
oldvalue = replaceAll("}", "}<br><br>",oldvalue);
		document.getElementById('editor').contentWindow.document.body.innerHTML  = oldvalue;

			console.log(document.getElementById('editor').contentWindow.document.body.innerHTML );

	//	cursorPosition = doGetCaretPosition(document.getElementById("editor"))-2;
		syntaxHighlighting('Hallo','blue');
		syntaxHighlighting('{','red');
		syntaxHighlighting('}','red');
brackets++;

	}
	//setPosition(4);
**/
//removeSyntaxHighlighting();
//for (var i=0; i<syntax.length; i++) {
  // syntaxHighlighting(syntax[i],'red');
//}
}

}
function replaceAll(find, replace, str) {
  return str.replace(new RegExp(find, 'g'), replace);
}
function removeSyntaxHighlighting(){
var textToChange = document.getElementById('editor').contentWindow.document.body.innerHTML;
textToChange = remove_tags(textToChange);
document.getElementById('editor').contentWindow.document.body.innerHTML = textToChange;
}
function syntaxHighlighting(code,color){
var textToHighlight = document.getElementById('editor').contentWindow.document.body.innerHTML;
var highlightedText = textToHighlight.replace(code,"<span style='color: "+color+";'>"+code+"</span>");
document.getElementById('editor').contentWindow.document.body.innerHTML = highlightedText;
}
function getCaretCharacterOffsetWithin(element) {
    var doc = element.ownerDocument || element.document;
    var win = doc.defaultView || doc.parentWindow;
    var sel, range, preCaretRange, caretOffset = 0;
    if (typeof win.getSelection != "undefined") {
        sel = win.getSelection();
        if (sel.rangeCount) {
            range = sel.getRangeAt(0);
            preCaretRange = range.cloneRange();
            preCaretRange.selectNodeContents(element);
            preCaretRange.setEnd(range.endContainer, range.endOffset);
            caretOffset = preCaretRange.toString().length;
        }
    } else if ( (sel = doc.selection) && sel.type != "Control") {
        range = doc.selection.createRange();
        preCaretRange = doc.body.createTextRange();
        preCaretRange.moveToElementText(element);
        preCaretRange.setEndPoint("EndToEnd", textRange);
        caretOffset = preCaretTextRange.text.length;
    }
    return caretOffset;
}
function remove_tags(html)
 {
   var html = html.replace("<br>","||br||");  
   var tmp = document.createElement("DIV");
   tmp.innerHTML = html;
   html = tmp.textContent||tmp.innerText;
   return html.replace("||br||","<br>");  
 }
function setPosition(index){
var o = document.getElementById('editor');
sel=o.contentWindow.getSelection();

//we are saving the current selected range obj
range2=sel.getRangeAt(0);

//and we need to create a new range object to set the caret position to 5
var range = document.createRange();

range.setStart(sel.anchorNode,index);

range.setEnd(sel.anchorNode,index);

//remove the old range and add the newly created range
sel.removeRange(range2);

sel.addRange(range);
}