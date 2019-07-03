function slugify(text) {
    return text.toString().toLowerCase()
        .replace(/\s+/g, '-')           // Replace spaces with -
        .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
        .replace(/\-\-+/g, '-')         // Replace multiple - with single -
        .replace(/^-+/, '')             // Trim - from start of text
        .replace(/-+$/, '');            // Trim - from end of text
}

$(document).ready(function () {
    let dropdown = $('#countries');

    dropdown.empty();

    dropdown.append('<option selected="true" disabled>Choose Country</option>');
    dropdown.prop('selectedIndex', 0);

    const url = '/static/countries.json';

    $.getJSON(url, function (data) {
        $.each(data, function (key, entry) {
            dropdown.append($('<option></option>').attr('value', (entry.country)).text(entry.country));
        })
    });
    $("#gotoCountry").click(function () {
        if (dropdown.val() != null) {
            console.log(dropdown.val());
            window.location.href = "/country?country=" + dropdown.val()
        } else {
            alert("Please Select Country");
            dropdown.focus();
        }
    })
});
