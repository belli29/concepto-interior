// switch to preorders
$('#switch-to-preorders').click(function () {
    $('#orders-section').toggle();
    $('#preorders-section').removeClass("d-none").show();
});
// switch to orders
$('#switch-to-orders').click(function () {
    $('#preorders-section').toggle();
    $('#orders-section').toggle();
});