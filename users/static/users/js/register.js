$(document).ready(function(){
    $("#id_username").focus(function(){
        $("#username_help_text").stop().slideDown(300);
    });

    $("#id_username").blur(function(){
        $("#username_help_text").stop().slideUp(300);
    });

    $("#id_password1").focus(function(){
        $("#password1_help_text").stop().slideDown(300);
    });

    $("#id_password1").blur(function(){
        $("#password1_help_text").stop().slideUp(300);
    });

    $("#id_password2").focus(function(){
        $("#password2_help_text").stop().slideDown(300);
    });

    $("#id_password2").blur(function(){
        $("#password2_help_text").stop().slideUp(300);
    });
});