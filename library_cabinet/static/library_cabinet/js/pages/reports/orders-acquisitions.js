$(function () {
    $("#id_status, #id_reader").select2({ width: '100%' });
    $("#id_date_from, #id_date_to").datepicker({
        format: "dd.mm.yyyy",
        language: "ru"
    });
});

$("#select-all-statuses").click(function(){
    $("#id_status > option").prop("selected", "selected");
    $("#id_status").trigger("change");
});

$("#select-all-readers").click(function(){
    $("#id_reader > option").prop("selected", "selected");
    $("#id_reader").trigger("change");
});
