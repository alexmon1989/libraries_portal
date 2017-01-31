var fillCitiesByRegionId = function (id) {
    $("#id_city").attr("disabled", true);
    $("#id_city").empty();
    $.getJSON( "/home/get-cities/" + $("#id_region").val() + '/', function( data ) {
        $.each(data, function (key, val) {
            $("#id_city").append( $('<option value="' + val[0] + '">' + val[1] + '</option>') );
        });
        $("#id_city").attr("disabled", false);
        $('#id_city').select2({ width: '100%' });

        fillLibrariesByCityId();
    });
};

var fillLibrariesByCityId = function (id) {
    $("#id_library").attr("disabled", true);
    $("#id_library").empty();
    $.getJSON( "/home/get-libraries-in-city/" + $("#id_city").val() + '/', function( data ) {
        $.each(data, function (key, val) {
            $("#id_library").append( $('<option value="' + val[0] + '">' + val[1] + '</option>') );
        });
        $("#id_library").attr("disabled", false);
        $('#id_library').select2({ width: '100%' });
    });
};

$(function () {
    $("#id_region, #id_city, #id_library").select2({ width: '100%' });

    $("#id_region").change(function () {
        fillCitiesByRegionId();
    });

    $("#id_city").change(function () {
        fillLibrariesByCityId();
    });
});