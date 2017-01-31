$(function () {
    $("#id_user").select2({ width: '100%' });
    $("#id_date_from, #id_date_to").datepicker({
        format: "dd.mm.yyyy",
        language: "ru"
    });
});

$("#select-all-users").click(function(){
    $("#id_user > option").prop("selected", "selected");
    $("#id_user").trigger("change");
});
