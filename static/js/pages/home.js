var fillUserFormCitiesByRegionId = function (id) {
    $("#form-user-registration #id_city").attr("disabled", true);
    $("#form-user-registration #id_city").empty();
    $.getJSON( "/home/get-cities/" + $("#form-user-registration #id_region").val() + '/', function( data ) {
        //$("#id_city").append( $('<option value=""></option>'));
        $.each(data, function (key, val) {
            $("#form-user-registration #id_city").append( $('<option value="' + val[0] + '">' + val[1] + '</option>') );
        });
        $("#form-user-registration #id_city").attr("disabled", false);
        $('#form-user-registration #id_city').select2({ width: '100%' });
    });
};

var fillLibraryFormCitiesByRegionId = function (id) {
    $("#form-library-registration #id_city").attr("disabled", true);
    $("#form-library-registration #id_city").empty();
    $.getJSON( "/home/get-cities/" + $("#form-library-registration #id_region").val() + '/', function( data ) {
        //$("#id_city").append( $('<option value=""></option>'));
        $.each(data, function (key, val) {
            $("#form-library-registration #id_city").append( $('<option value="' + val[0] + '">' + val[1] + '</option>') );
        });
        $("#form-library-registration #id_city").attr("disabled", false);
        $('#form-library-registration #id_city').select2({ width: '100%' });
    });
};

var fillLibraryKindsByLibraryTypeId = function (id) {
    $("#form-library-registration #id_library_kind").attr("disabled", true);
    $("#form-library-registration #id_library_kind").empty();
    $.getJSON( "/home/get-library-kinds/" + $("#form-library-registration #id_library_type").val() + '/', function( data ) {
        //$("#id_library_kind").append( $('<option value=""></option>'));
        $.each(data, function (key, val) {
            $("#form-library-registration #id_library_kind").append( $('<option value="' + val[0] + '">' + val[1] + '</option>') );
        });
        $("#form-library-registration #id_library_kind").attr("disabled", false);
        $("#form-library-registration #id_library_kind").select2({ width: '100%' });
    });
};

$(function () {
    $("#form-user-registration #id_region").select2({ width: '100%' });
    $("#form-user-registration #id_city").select2({ width: '100%' });
    $("#form-library-registration #id_region").select2({ width: '100%' });
    $("#form-library-registration #id_city").select2({ width: '100%' });
    $("#form-library-registration #id_library_type").select2({ width: '100%' });
    $("#form-library-registration #id_library_kind").select2({ width: '100%' });

    $("#form-user-registration #id_region").change(function () {
        fillUserFormCitiesByRegionId();
    });

    $("#form-library-registration #id_region").change(function () {
        fillLibraryFormCitiesByRegionId();
    });

    $("#form-library-registration #id_library_type").change(function () {
        fillLibraryKindsByLibraryTypeId();
    });
});