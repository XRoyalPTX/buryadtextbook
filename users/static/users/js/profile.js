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
});