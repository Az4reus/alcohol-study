/**
 * Created by az on 28/04/16.
 */

var addTextbox = function (id) {
    var e = document.getElementById(id).parentNode;
    var textbox = document.getElementById('q1_textbox');
    var labelbox = $('#labelBox');

    if (textbox == null) {
        var label = document.createElement('label');
        var text = document.createTextNode('Please specify: ');
        label.appendChild(text);
        label.setAttribute('id', 'labelBox');

        var box = document.createElement("input");
        box.setAttribute('type', 'text');
        box.setAttribute('name', 'q1_textbox');
        box.setAttribute('id', 'q1_textbox');

        label.appendChild(box);
        e.appendChild(label);

    } else if (labelbox !== null && labelbox.parentNode !== e) {
        e.appendChild(labelbox[0]);
    }
};

var validateSurveyInputs = function () {
    cleanUpSurvey();
    var valid = true;

    // Q1 needs validation that the textbox is filled when
    // 'family' or 'other' are selected.
    var q1 = $('input[name=q1]:checked').val();

    if (q1 === undefined) {
        valid = false;
        attachAlert('q1_container')

    } else if (q1 === 'A family member' || q1 === 'other') {
        var textbox = $("#q1_textbox");

        if (textbox.val() === "") {
            valid = false;
            attachAlert("q1_container");
        }
    }

    // Q2 just needs confirmation that it's not empty and that
    // it's actually a number.
    var q2 = $("#q2_box");
    if (q2.val() === '') {
        valid = false;
        attachAlert('q2_container');
    }

    // Starts with one or more digits, optionally has a dot or a comma
    // as separator, then has one or more digits after that, plus whitespace
    // at the end.
    var allowedFormat = /^\d+[\.,]?\d*\s*$/;
    if (valid === true && !allowedFormat.test(q2.val())) {
        valid = false;
        attachAlert('q2_container');
    }

    // Now for Q3-12, the validation logic is always the same, so
    // might as well loop through it.
    var ids = ["q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12"];
    for (var i = 0; i < ids.length; i++) {
        var e = ids[i];
        var elem = $("select[name=" + e + "]");

        if (elem.val() === 'nil') {
            valid = false;
            attachAlert(e + '_container');
        }
    }

    // If everything is lovely and pretty,
    // press the hidden submit button.
    if (valid === true) {
        $("#actualButton").click();
    }
};

var validateNfSurveyInputs = function (unfocusedPeople) {
    // First, remove any potential old alerts.
    cleanUpNfSurvey();
    var valid = true;
    unfocusedPeople = parseInt(unfocusedPeople);

    // The inputs for every question must add up to the amount of
    // unfocused people in the picture. That's what we need to check.

    var q1Containers = ['q1_spouse', 'q1_family', 'q1_close_friend',
        'q1_friend', 'q1_acquaintance', 'q1_coworker', 'q1_stranger',
        'q1_other'];
    var q2Containers = ['q2_less1mo', 'q2_less6mo', 'q2_less1y',
        'q2_1-2y', 'q2_3-5y', 'q2_more5y'];
    var q3Containers = ['q3_0-2', 'q3_2-10', 'q3_10-20', 'q3_20-50',
        'q3_50-100', 'q3_100-200', 'q3_200-500', 'q3_500-1k', 'q3_1k-5k',
        'q3_5k-10k', 'q3_10k_plus'];

    var q1Sum = 0;
    for (var q1 = 0; q1 < q1Containers.length; q1++) {
        q1Sum += parseInt($('#' + q1Containers[q1]).val());
    }
    if (q1Sum !== unfocusedPeople) {
        attachAlert('q1_container');
        valid = false;
    }

    var q2Sum = 0;
    for (var q2 = 0; q2 < q2Containers.length; q2++) {
        q2Sum += parseInt($('#' + q2Containers[q2]).val());
    }
    if (q2Sum !== unfocusedPeople) {
        attachAlert('q2_container');
        valid = false;
    }

    var q3Sum = 0;
    for (var q3 = 0; q3 < q3Containers.length; q3++) {
        q3Sum += parseInt($('#' + q3Containers[q3]).val());
    }
    if (q3Sum !== unfocusedPeople) {
        attachAlert('q3_container');
        valid = false;
    }

    // If all is lovely and it adds up, press the button.
    if (valid === true) {
        $('#actualButton').click();
    }

};

var attachAlert = function (elementId) {
    $('#' + elementId)
        .addClass("alert")
        .addClass('alert-danger');
};

var cleanUpSurvey = function () {
    var containers = [];
    for (var i = 1; i < 13; i++) {
        containers.push("q" + i + '_container');
    }

    for (var j = 0; j < containers.length; j++) {
        $('#' + containers[j])
            .removeClass('alert')
            .removeClass('alert-danger');
    }
};

var cleanUpNfSurvey = function () {
    var containers = ['q1_container', 'q2_container', 'q3_container'];
    for (var i = 0; i < containers.length; i++) {
        $('#' + containers[i])
            .removeClass('alert')
            .removeClass('alert-danger');
    }
};