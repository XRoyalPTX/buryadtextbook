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

    async function getRussianTranslate() {
        let $container = $("#id_russian-translations");
        $container.empty();
        try {
            let wordToTranslate = $("#id_random-buryad-word").data("word");
            let url = `https://burlang.ru/api/v1/buryat-word/translate?q=${wordToTranslate}`;
            let response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            let data = await response.json();
            let translations = data.translations;

            if (translations && translations.length > 0) {
                translations.forEach(function(elem) {
                    console.log(elem.value);
                    $container.append(`<span style="display: block;">${elem.value}</span>`);
                });
            } else {
                $container.text("Перевод не найден");
            }

        } catch (error) {
            console.log(`There's Error: ${error.message}`);
            $container.append(`<span style="display: block;">Не удалось загрузить перевод (слово не найдено)</span>`);
        }
    }

    getRussianTranslate();

    $("#id_random-buryad-word").click(function() {
        let $tip = $("#id_random-buryad-word-tip");
        let $translations = $("#id_russian-translations");

        $tip.stop(true, true);
        $translations.stop(true, true);

        if ($translations.is(':visible')) {
            $tip.fadeOut(300, function() {
                $(this).text('Нажмите на слово, чтобы открыть перевод').fadeIn(300);
            });
        } else {
            $tip.fadeOut(300, function() {
                $(this).text('Нажмите снова, чтобы закрыть перевод').fadeIn(300);
            });
        }

        $translations.slideToggle(300);
    });
});