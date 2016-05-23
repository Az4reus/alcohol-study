/**
 * Created by az on 28/04/16.
 */

var addTextbox = function (id) {
    var e = document.getElementById(id).parentNode;
    var textbox = document.getElementById(id + '_textbox');

    if (textbox == null) {
        var label = document.createElement('label');
        var text = document.createTextNode('Please specify: ');
        label.appendChild(text);

        var box = document.createElement("input");
        box.setAttribute('type', 'text');
        box.setAttribute('name', 'q1_textbox');
        box.setAttribute('id', 'q1_textbox');

        label.appendChild(box);
        e.appendChild(label);
    }
};

var validateSurveyInputs = function () {
    cleanUp();
    var valid = true;

    // Q1 needs validation that the textbox is filled when
    // 'family' or 'other' are selected.
    var q1 = $('input[name=q1]:checked').val();
    if (q1 === 'A family member' || q1 === 'other') {
        var textbox = $("#q1_textbox");

        if (textbox.val() === "") {
            valid = false;
            signifyAlert("q1_container");
        }
    }

    // Q2 just needs confirmation that it's not empty and that
    // it's actually a number.
    var q2 = $("#q2_box");
    if (q2.val() === '') {
        valid = false;
        signifyAlert('q2_container');
    }

    // Starts with one or more digits, optionally has a dot or a comma
    // as separator, then has one or more digits after that, plus whitespace
    // at the end.
    var allowedFormat = /^\d+[\.,]?\d*\s*$/;
    if (valid === true && !allowedFormat.test(q2.val())) {
        valid = false;
        signifyAlert('q2_container');
    }

    // Now for Q3-12, the validation logic is always the same, so
    // might as well loop through it.
    var ids = ["q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12"];
    for (var i = 0; i < ids.length; i++) {
        var e = ids[i];
        var elem = $("select[name=" + e + "]");

        if (elem.val() === 'nil') {
            valid = false;
            signifyAlert(e + '_container');
        }
    }

    // If everything is lovely and pretty,
    // press the hidden submit button.
    if (valid === true) {
        alert('what the fuck');
        $("#actualButton").click();
    }
};

var validateNfSurveyInputs = function (unfocusedPeople) {

};

var signifyAlert = function (elementId) {
    $('#' + elementId).addClass("alert").addClass('alert-danger');
};

var cleanUp = function () {
    var containers = [];
    for (var i = 1; i < 13; i++) {
        containers.push("q" + i + '_container');
    }

    for (var j = 0; j < containers.length; j++) {
        $('#' + containers[j]).removeClass('alert').removeClass('alert-danger');
    }
};