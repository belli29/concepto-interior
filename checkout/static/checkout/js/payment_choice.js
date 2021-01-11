// payment options UI 
$('.payment-option').click(function () {
    $(this).addClass("text-color-pr");
    var other_methods = $(this).closest('.row').find('.payment-option').not(this);
    $(other_methods).removeClass("text-color-pr");
});
// Paypal payment
$('#paypal-payment').click(function () { 
    $("#payment-choice").val("paypal"); // alter value of payment-choice form field
    $(".paypal-total").removeClass("d-none"); // display discounted total
    $(".checkout-total").css("text-decoration", "line-through");// total barred 
    $("#paypal_p").removeClass("d-none");// display paypal payment info
    $("#card-element,#card-errors").addClass("d-none");// remove Stripe cc field
    $("#submit-button").removeClass("d-none").html("<span class='text-uppercase'>get invoice </span><span class='icon'><i class='fas fa-chevron-right'></i></span>");
});
// Stripe payment
$('#stripe-payment').click(function () { 
    // call view to create stripe intent
    var url = "/checkout/";
    var data = { "payment-choice" : "stripe"};
    $.get(url,data);
    $("#payment-choice").val("stripe"); // alter value of payment-choice form field
    $(".paypal-total").addClass("d-none");// hide discounted total
    $(".checkout-total").css("text-decoration", "none");// total unbarred 
    $("#card-element").removeClass("d-none");// display Stripe cc field 
    $("#paypal_p").addClass("d-none");// remove paypal payment info
    $("#submit-button").removeClass("d-none").html("<span class='text-uppercase'>secure checkout</span><span class='icon'><i class='fas fa-lock'></i></span>");
});