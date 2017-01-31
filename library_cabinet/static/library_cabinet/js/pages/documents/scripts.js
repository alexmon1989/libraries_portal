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
                .attr("selected", "selected")
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
                .attr("selected", "selected")
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