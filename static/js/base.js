$(document).ready(function(){
    $(".alert").click(function(){
        $(this).fadeTo(400, 0.5).slideUp(400, function(){
            $(this).remove();
        });
    });

    setTimeout(function() {
        $(".alert").fadeTo(400, 0.5).slideUp(400, function(){
            $(this).remove();
        });
    }, 5000);
});