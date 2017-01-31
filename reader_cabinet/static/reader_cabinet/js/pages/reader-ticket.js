var fillUserFormCitiesByRegionId = function (id) {
    $("#id_city").attr("disabled", true);
    $("#id_city").empty();
    $.getJSON( "/home/get-cities/" + $("#id_region").val() + '/', function( data ) {
        $.each(data, function (key, val) {
            $("#id_city").append( $('<option value="' + val[0] + '">' + val[1] + '</option>') );
        });
        $("#id_city").attr("disabled", false);
        $('#id_city').select2({ width: '100%' });
    });
};

$(function () {
    $("#id_region, #id_city").select2({ width: '100%' });

    $("#id_region").change(function () {
        fillUserFormCitiesByRegionId();
    });
});