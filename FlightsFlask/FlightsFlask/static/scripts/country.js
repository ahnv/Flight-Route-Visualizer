$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    return decodeURI(results[1]) || 0;
}

$(document).ready(function () {
    var country = $.urlParam('country');
    if (country == null || country == "") {
        alert("Country missing");
        window.location.href = "/"
    }

    $("#country").html(country);
    $.get('/api/country_process', { country: country })
        .done(function (response) {
            if (response.simple == 1) {
                $("#map1").attr("src", '/static/images/' + country + '/map_1.png');
                $("#map2").attr("src", '/static/images/' + country + '/map_2.png');
            }
            if (response.advanced == 1) {
                $("#map3").attr("src", '/static/images/' + country + '/map_3.png');
            }
            $("#stats").html(JSON.stringify(response.stats, 2));
        });
    
    

})