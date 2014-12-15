/*
@author: Thore Thießen
@creation: 11.12.2014 - sprint-nr: 3
@last-change: 12.12.2014 - sprint-nr: 3
*/

/**
 * Erstellt einen neuen ListSelector, mit dem Daten dargestellt und aus ihnen ausgewählt werden 
 * kann.
 * @param containerId ID des Containers, in dem der ListSelector enthalten sein soll
 */
function ListSelector(containerId) {
	// ID des Containers
	var id = containerId;

	// Bezeichner für die darzustellenden Datenelemente; [{name: '…', element: '…'}, …]
	var captions = [];

	/**
	 * Fügt einen Bezeichner für ein Element der Daten hinzu.
	 * @param name Bezeichnung für die Elemente (in der Überschrift)
	 * @param element Element, dessen Wert angezeigt werden sollen (Tabelleninhalt)
	 * @param render bei <code>true</code> wird das DOM neu gerendert
	 */
	this.addCaption = function(name, element, render) {
		if (typeof name == 'string' && typeof element == 'string')
			captions.push({'name': name, 'element': element});
		if (render)
			this.render();
	};

	/**
	 * Setzt die Bezeichner für die anzuzeigenden Elemente der Datensätze.
	 * @param newCaptions Array von Paaren aus Bezeichner (name) und Element (element)
	 */
	this.setCaptions = function(newCaptions) {
		captions.length = 0;
		$.each(newCaptions, function(i, e) {
			if (typeof e.name == 'string' && typeof e.element == 'string')
				captions.push({'name': e.name, 'element': e.element});
		});
		this.render();
	};

	// Datensätze; [{object: {element1: …, …}, children: [{…}, …], show: true/false}, …]
	var data = [];

	/**
	 * Löscht alle Datensätze.
	 */
	this.clearData = function() {
		data.length = 0;
		selected = null;
		this.render();
	};

	// gibt die Datenstruktur an einem bestimmen Pfad oder null
	function atPath(path) {
		if (path != null && $.isArray(path) && path.length > 0) {
			var result;

			if (path[0] % 1 === 0 && path[0] < data.length)
				result = data[path[0]];
			else
				return(null);

			for (var i = 1; i < path.length; ++i)
				if (path[i] % 1 === 0 && path[i] < result.children.length)
					result = result.children[path[i]];
				else
					return(null);

			return(result);
		} else
			return(null);
	}

	/**
	 * Fügt einen neuen Datensatz ein.
	 * @param object Datensatz
	 * @param path Pfad, an welcher Stelle der Datensatz in der Struktur eingefügt werden soll
	 * @param show bei <code>true</code> ist der Unterbaum anfänglich aufgeklappt
	 * @param render bei <code>true</code> wird das DOM neu gerendert
	 * @return relativer Index des neu eingefügten Datensatzes
	 */
	this.addData = function(object, path, show, render) {
		if (typeof object == 'object') {
			path = typeof path !== 'undefined' ? path : [];
			show = typeof show !== 'undefined' ? show : true;
			render = typeof render !== 'undefined' ? render : true;
	
			// zur richtigen Stelle in der Datenstruktur wechseln
			var container = atPath(path);
			if (container == null)
				container = data;
			else
				container = container.children;
	
			// Objekt einfügen
			var index = container.push({'object': object, 'children': [], 'show': show}) - 1;
	
			// ggf. DOM neu rendern
			if (render)
				this.render();
	
			return(index);
		} else
			return(-1);
	}

	// wandelt einen Pfad in eine HTML-ID um
	function pathToId(path) {
		var result = 'ls_' + id;
		for (var i = 0; i < path.length; ++i)
			result += '_' + path[i];
		return(result);
	}

	// Anzahl der Pixel, um die eine Ebene verschoben werden soll
	var indent = 15;

	// gibt alle Elemente einer Ebene und der darunter liegenden Ebenen aus
	function renderElements(container, path, output, object) {
		for (var i = 0; i < container.length; ++i) {
			// Pfad für das aktuelle Element
			var currPath = path.slice();
			currPath.push(i);

			// Tabellenreihe für das Element
			var row = $('<tr></tr>').attr('id', pathToId(currPath));
			output.append(row);

			// ausgewähltes Element hinterlegen
			if (selected != null && currPath.length == selected.length) {
				var same = true;
				for (var j = 0; j < currPath.length; ++j) {
					if (currPath[j] != selected[j])
						same = false;
						break;
					}
				if  (same)
					row.addClass('selected');
			}

			// Auf- und Einklappfunktionalität
			var cell = $('<td></td>');
			row.append(cell);
			if (container[i].children.length > 0) {
				if (container[i].show)
					cell.text('-');
				else
					cell.text('+');
				cell.click({'object': object, 'path': currPath}, function(event) {
					event.data.object.toggleShow(event.data.path);
				});
			}

			// anzuzeigende Elemente hinzufügen
			for (var j = 0; j < captions.length; ++j) {
				var cell = $('<td></td>').text(container[i].object[captions[j].element]);
				if (j == 0)
					cell.attr('style', 'padding-left: ' + path.length * indent + 'px');
				row.append(cell);
			}

			// Auswahlklick behandeln
			row.click({'object': object, 'path': currPath}, function(event) {
				event.data.object.setSelected(event.data.path);
			});

			// Doppelklick behandeln
			row.dblclick({'object': object, 'path': currPath}, function(event) {
				event.data.object.dClick(event.data.path);
			});

			// ggf. Unterelemente anzeigen
			if (container[i].children.length > 0 && container[i].show)
				renderElements(container[i].children, currPath, output, object);
		}
	}

	/**
	 * Aktualisiert den HTML-Code entsprechend der vorliegenden Daten.
	 */
	this.render = function() {
		var table = $('<table></table>').addClass('listSelector');
		$('#' + id).html(table);

		// Überschriften
		var heading = $('<tr></tr>').append('<td></td>');
		table.append($('<thead></thead>').append(heading));
		for (var i = 0; i < captions.length; ++i)
			heading.append($('<td></td>').text(captions[i].name));

		// Datensätze
		var tbody = $('<tbody></tbody>');
		table.append(tbody);
		renderElements(data, [], tbody, this);
	};

	// Pfad zum ausgewählten Datensatz
	var selected = null;

	/**
	 * Gibt den ausgewählten Datensatz.
	 * @return ausgewählter Datensatz oder <code>null</code>
	 */
	this.getSelected = function() {
		var result = atPath(selected);
		if (result != null)
			return(result.object);
		else
			return(null);
	};

	/**
	 * Setzt den ausgewählten Datensatz.
	 * @param path Pfad zum auszuwählenden Datensatz oder <code>null</code>, um keinen Datensatz 
	 * auszuwählen
	 */
	this.setSelected = function(path) {
		// ggf. Markierung an alter Auswahl entfernen
		if (selected != null)
			$('#' + pathToId(selected)).removeClass('selected');

		if (atPath(path) != null)
			selected = path;
		else
			selected = null;

		// ggf. neue Auswahl markieren
		if (selected != null)
			$('#' + pathToId(selected)).addClass('selected');
	};

	/**
	 * Klappt die Unterpunkte eines Punktes aus oder ein.
	 * @param path Pfad zum Punkt
	 */
	this.toggleShow = function(path) {
		var object = atPath(path);
		if (object != null)
			object.show = !object.show;
		this.setSelected(null);
		this.render();
	};

	// Funktion, die bei Doppelklick auf einen Datensatz aufgerufen wird
	var dClickHandler = function(object) {};

	/**
	 * Behandelt einen Doppelklick auf einen Datensatz.
	 * @param path Pfad zum Datensatz
	 */
	this.dClick = function(path) {
		var object = atPath(path);
		if (object != null)
			dClickHandler(object.object);
	};

	/**
	 * Setzt den Handler für einen Doppelklick auf einen Datensatz.
	 * @param handler Funktion, die bei Doppelklick mit dem Datensatzes als Parameter aufgerufen 
	 * wird
	 */
	this.setDClickHandler = function(handler) {
		dClickHandler = handler;
	};
}
