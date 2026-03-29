$(document).ready(function(){
    function hideAlert($alert) {
        $alert.fadeTo(400, 0.5).slideUp(400, function(){
            $(this).remove();
        });
    }

    $(document).on('click', '.alert', function(){
        hideAlert($(this));
    });

    setTimeout(function() {
        hideAlert($(".alert"));
    }, 5000);

    document.body.addEventListener('htmx:afterSwap', function() {
        let newAlerts = $('#id_messages-container .alert');
        if (newAlerts.length > 0) {
            setTimeout(function() {
                hideAlert(newAlerts);
            }, 5000);
        }
    });
});