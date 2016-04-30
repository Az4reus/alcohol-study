/**
 * Created by az on 28/04/16.
 */

var addTextbox = function (id) {
    var e = document.getElementById(id).parentNode;

    var label = document.createElement('label');
    var text = document.createTextNode('Please specify:       ');
    label.appendChild(text);

    var box = document.createElement("input");
    box.setAttribute('type', 'text');
    box.setAttribute('name', id+'_textbox');

    label.appendChild(box);
    e.appendChild(label);
};