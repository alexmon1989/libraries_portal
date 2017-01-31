var fillFormCitiesByRegionId = function () {
    $("#id_city").attr("disabled", true);
    $("#id_city").empty();
    $.getJSON( "/home/get-cities/" + $("#id_region").val() + '/', function( data ) {
        //$("#id_city").append( $('<option value=""></option>'));
        $.each(data, function (key, val) {
            $("#id_city").append( $('<option value="' + val[0] + '">' + val[1] + '</option>') );
        });
        $("#id_city").attr("disabled", false);
        $('#id_city').select2({ width: '100%' });
    });
};

var fillLibraryKindsByLibraryTypeId = function () {
    $("#id_library_kind").attr("disabled", true);
    $("#id_library_kind").empty();
    $.getJSON( "/home/get-library-kinds/" + $("#id_library_type").val() + '/', function( data ) {
        //$("#id_library_kind").append( $('<option value=""></option>'));
        $.each(data, function (key, val) {
            $("#id_library_kind").append( $('<option value="' + val[0] + '">' + val[1] + '</option>') );
        });
        $("#id_library_kind").attr("disabled", false);
        $("#id_library_kind").select2({ width: '100%' });
    });
};

$(function () {
    $("#id_region, #id_city, #id_library_type, #id_library_kind").select2({ width: '100%' });

    $("#id_region").change(function () {
        fillFormCitiesByRegionId();
    });

    $("#id_library_type").change(function () {
        fillLibraryKindsByLibraryTypeId();
    });
});