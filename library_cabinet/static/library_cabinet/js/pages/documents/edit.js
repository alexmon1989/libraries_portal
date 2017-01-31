function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

addAnotherPerson = function (name) {
    var newAnotherPersonName = $("#new-another-person-name").val();

    $.post( "/library-cabinet/another-persons/add/", { name: newAnotherPersonName }, function(data) {
        if (data.success == false) {
            $(".errors").html(data.errors);
        } else {
            $("#add-another-person-modal").modal("hide");
            $("#new-another-person-name").val("");
            $(".errors").html('');

            $("#id_another_persons").select2("destroy");
            $("#id_another_persons").append($("<option></option>")
                .attr("value", data.id)
                .text(newAnotherPersonName));
            $("#id_another_persons").select2({ width: '100%' });
        }
    });
};

addRubric = function (name) {
    var newRubricName = $("#new-rubric-name").val();

    $.post( "/library-cabinet/rubrics/add/", { name: newRubricName }, function(data) {
        if (data.success == false) {
            $(".errors").html(data.errors);
        } else {
            $("#add-rubric-modal").modal("hide");
            $("#new-rubric-name").val("");
            $(".errors").html('');

            $("#id_rubrics").select2("destroy");
            $("#id_rubrics").append($("<option></option>")
                .attr("value", data.id)
                .text(newRubricName));
            $("#id_rubrics").select2({ width: '100%' });
        }
    });
};

$(function () {
    $("#id_rubrics, #id_another_persons").select2({ width: '100%' });
    $("#add-another-person-submit").click(addAnotherPerson);
    $("#add-rubric-submit").click(addRubric);
});