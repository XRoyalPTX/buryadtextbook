$(document).ready(function() {
    $("#id_profile-card-btn-dlt").click(function(event) {
        let result = confirm('Вы точно хотите удалить аккаунт?\nЭто повлечет за собой удаление всех данных!');
        if (!result) {
            event.preventDefault();
            console.log('Удаление аккаунт прервано.')
        } else {
            console.log('Аккаунт удалён пользователем.');
        }
    });

    $("#id_random-buryad-word").click(function() {
        let currentText = $("#id_random-buryad-word-tip").text();
        if (currentText.includes('открыть')) {
            $("#id_random-buryad-word-tip").stop().fadeOut(500, function(){
                $("#id_random-buryad-word-tip").text('Нажмите снова, чтобы закрыть перевод');
                $("#id_random-buryad-word-tip").stop().fadeIn(500);
            });
        } else {
            $("#id_random-buryad-word-tip").stop().fadeOut(500, function(){
                $("#id_random-buryad-word-tip").text('Нажмите на слово, чтобы открыть перевод');
                $("#id_random-buryad-word-tip").stop().fadeIn(500);
            });
        }
        $("#id_russian-translations").stop().slideToggle(500);
    });
});