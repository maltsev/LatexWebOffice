/*
@author: Thore Thießen
@creation: 01.12.2014 - sprint-nr: 2
@last-change: 01.12.2014 - sprint-nr: 2
*/

/**
 * Enkodiert eine Zeichenkette HTML-sicher.
 * @param string Zeichenkette
 * @returns enkodierte Zeichenkette
 */
function htmlEscape(string) {
	return(String(string)
			.replace(/&/g, '&amp;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;'));
}

/**
 * Leitet den Benutzer auf eine Seite weiter, wobei zusätzlich POST-Daten gesendet werden.
 * @param url URL der Seite
 * @param data Daten
 */
function postRedirect(url, data) {
	var formHtml = '<form action="' + url + '" method="post">';
	$.each(data, function(index, value) {
		formHtml += '<input type="hidden" name="' + htmlEscape(index) + '" value="' + 
				htmlEscape(value) + '" />';
	});
	var form = $(formHtml);
	$('body').append(form);
	form.submit();
}
