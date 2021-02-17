/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
*/
// mounts card element
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: '#f1089e',
        
        fontSmoothing: 'antialiased',
        
        '::placeholder': {
            
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card-element');

// displays error message
card.on('change', function(event) {
  var displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
});

// handles form submit
var form = document.getElementById('payment-form');
var paymentChoice = document.getElementById('payment-choice');
form.addEventListener('submit', function(ev) {
    if (paymentChoice.value =='stripe' || paymentChoice.value =='oxxo' ){
        ev.preventDefault();
        card.update({ 'disabled': true});
        $('#submit-button').attr('disabled', true);
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);
        $('#submit-button').attr('disabled', true);

        // call cache_checkout_data view
        var saveInfo = Boolean($('#id-save-info').attr('checked'));
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        var url ='/checkout/cache_checkout_data/';
        var postData = {
            'save_info': saveInfo,
            'client_secret' : clientSecret,
            'csrfmiddlewaretoken': csrfToken,
        };
        if (paymentChoice.value =='stripe'){ // when user wants to pay by cc
            $.post(url, postData).done( function (){
                stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: $.trim(form.full_name.value),
                        phone: $.trim(form.phone_number.value),
                        email: $.trim(form.email.value),
                        address: {
                            line1: $.trim(form.street_address1.value),
                            line2: $.trim(form.street_address2.value),
                            city: $.trim(form.town_or_city.value),
                            country: $.trim(form.country.value),
                            state: $.trim(form.county.value),
                        }
                    }
                },
                shipping: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    address: {
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        postal_code: $.trim(form.postcode.value),
                        state: $.trim(form.county.value),
                    }
                }
                }).then(function(result) {
                    console.log("go1")
                    if (result.error) {
                        var errorDiv = document.getElementById('card-errors');
                        var html = `
                            <span class="icon" role="alert">
                            <i class="fas fa-times"></i>
                            </span>
                            <span>${result.error.message}</span>`;
                        $(errorDiv).html(html);
                        $('#payment-form').fadeToggle(100);
                        $('#loading-overlay').fadeToggle(100);
                        card.update({ 'disabled': false});
                        $('#submit-button').attr('disabled', false);
                    } else {
                        if (result.paymentIntent.status === 'succeeded') {
                            console.log("go2")
                            form.submit();
                        }
                    }
                });
            }).fail(function(){
                //reloads the page, error message triggered by view will be displayed
                location.reload();
            })             
        }else{ // when user wants to pay by oxxo
            console.log("here0")
            $.post(url, postData).done( function (){
                console.log("here1");
                stripe.confirmOxxoPayment(
                    clientSecret,
                    {
                        payment_method: {
                            billing_details: {
                                name: $.trim(form.full_name.value),
                                email: $.trim(form.email.value),
                            }
                        },
                        shipping: {
                            name: $.trim(form.full_name.value),
                            phone: $.trim(form.phone_number.value),
                            address: {
                                line1: $.trim(form.street_address1.value),
                                line2: $.trim(form.street_address2.value),
                                city: $.trim(form.town_or_city.value),
                                country: $.trim(form.country.value),
                                postal_code: $.trim(form.postcode.value),
                                state: $.trim(form.county.value),
                            }
                        },
                        receipt_email: $.trim(form.email.value)
                    })
                .then(function(result) {
                // This promise resolves when the customer closes the modal
                console.log("here2");
                if (result.error){
                    // Display error to your customer
                    var errorMsg = document.getElementById('oxxo-error-message');
                    errorMsg.innerText = result.error.message;
                    console.log(" error should be displayed")
                    $('#loading-overlay').fadeToggle(100);
                    $('#submit-button').attr('disabled', false);
                    $('#payment-form').fadeToggle(100);
                }else{
                    console.log("here3");
                    form.submit();                    
                }
                });
            });
        };
    };
});
