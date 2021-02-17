// payment options UI 
$('.payment-option').click(function () {
    $(this).addClass("text-color-pr");
    var other_methods = $(this).closest('.row').find('.payment-option').not(this);
    $(other_methods).removeClass("text-color-pr");
});

paypalParagraph = $("#paypal_p")
oxxolParagraph = $("#oxxo_p, #oxxo-error-message")
// Paypal payment
$('#paypal-payment').click(function () {
    $("#payment-choice").val("paypal"); // alter value of payment-choice form field
    $(".paypal-total").removeClass("d-none"); // display discounted total
    $(".checkout-total").css("text-decoration", "line-through");// total barred 
    paypalParagraph.removeClass("d-none");// display paypal payment info
    $("#card-element,#card-errors").addClass("d-none");// remove Stripe cc field
    oxxolParagraph.addClass("d-none");// remove Oxxo paragraph
    $("#submit-button").removeClass("d-none").html("<span class='text-uppercase'> Factura PayPal </span><span class='icon'><i class='fas fa-chevron-right'></i></span>");
});
// Oxxo payment
$('#oxxo-payment').click(function () { 
    $("#payment-choice").val("oxxo"); // alter value of payment-choice form field
    $(".paypal-total").addClass("d-none");// hide discounted total
    $(".checkout-total").css("text-decoration", "none");// total unbarred 
    oxxolParagraph.removeClass("d-none");// display Oxxo p
    paypalParagraph.addClass("d-none");// remove paypal payment info
    $("#card-element,#card-errors").addClass("d-none");// remove Stripe cc field
    $("#submit-button").removeClass("d-none").html("<span class='text-uppercase'> Recibe codigo QR </span><span class='icon'><i class='fas fa-chevron-right'></i></span>");
});
// Stripe payment
$('#stripe-payment').click(function () { 
    // call view to create stripe intent
    $("#payment-choice").val("stripe"); // alter value of payment-choice form field
    $(".paypal-total").addClass("d-none");// hide discounted total
    $(".checkout-total").css("text-decoration", "none");// total unbarred 
    $("#card-element").removeClass("d-none");// display Stripe cc field 
    paypalParagraph.addClass("d-none");// remove paypal payment info
    oxxolParagraph.addClass("d-none");// remove Oxxo p
    $("#submit-button").removeClass("d-none").html("<span class='text-uppercase'>Pago Seguro</span><span class='icon ml-3'><i class='fab fa-stripe'></i></span>");
});