/**
 * Created by az on 24/04/16.
 */
"use strict";

var hiddenControl = function () {
    var radioValue = window.document.getElementById('containsPeople').value;
    var hidden = window.document.getElementById('hiddenControl');

    if(radioValue == 'Yes') {
        hidden.className = "";
    } else {
        hidden.className = "hidden";
    }
};