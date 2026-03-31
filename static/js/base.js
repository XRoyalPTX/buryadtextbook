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

    $("#burger-toggle").on('click', function(){
        $(this).toggleClass('open');
        $('.mobile-menu').stop(true, true).slideToggle(300);
    });

    $(document).on('click', function(e){
        if (($(e.target).closest('.mobile-menu').length === 0) && ($(e.target).closest('#burger-toggle').length === 0)) {
            $('.mobile-menu').slideUp(300);
            $('#burger-toggle').removeClass('open');
        };
    });

});