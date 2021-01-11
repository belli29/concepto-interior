
// check if the new shiping destination creates problems and recalculates shipping fees
$('select[name="country"]').change( function(){
        // colleting current delivery selection
        var getData = {
                'full_name': $('input[name="full_name"]').val(),
                'email': $('input[name="email"]').val(),
                'phone_number': $('input[name="phone_number"]').val(),
                'country': $('select[name="country"]').val(),
                'postcode': $('input[name="postcode"]').val(),
                'town_or_city': $('input[name="town_or_city"]').val(),
                'street_address1': $('input[name="street_address1"]').val(),
                'street_address2': $('input[name="street_address2"]').val(),
                'county': $('input[name="county"]').val(),
            };
        var parameters = $.param( getData );
        window.location.href = `/checkout/?${parameters}`;
    })

// avoid displaying error messages in case of change country

$( document ).ready(function() {
    changeCountry = $('#change_country').text()
    console.log(changeCountry);
    if (changeCountry=='True'){
        $('input').removeClass("is-invalid");
        $('#change_country').text("False");
        // delete session variable chosen country in order to avoid possible conflicts with standard deliver address of logged in users
        url="/checkout/delete_session_chosen_country";
        $.get(url);
    }   
});
