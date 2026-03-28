$(document).ready(function(){
    $("input, textarea").focus(function(){
        var helper = "#" + $(this).attr('id') + "-help";
        $(helper).stop().slideDown(300);
    });

    $("input, textarea").blur(function(){
        var helper = '#' + $(this).attr('id') + '-help';
        $(helper).stop().slideUp(300);
    });
});