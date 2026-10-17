$(document).ready(function(){

    let $app = $("#dictionary-app");
    let textBur = $app.data('placeholder-bur') || 'Введите слово на бурятском';
    let textRus = $app.data('placeholder-rus') || 'Введите слово на русском';
    let initialText = $app.data('initial-text') || 'Тут появится найденный перевод слова.';
    let notFoundText = $app.data('not-found') || 'Ой... Видимо, такого слова ещё нет в словаре.';
    let serverErrorText = $app.data('server-error') || 'Произошла ошибка сервера.';

    let $isBuryadToRussian = true;
    let $fromToText = $("#from-to");
    let $input = $("#word-input");
    let $container = $("#id_translations");
    let isDefaultText = true;

    $("#from-bur-to-rus").on('click', function(){
        $(this).addClass('active');
        $("#from-rus-to-bur").removeClass('active');
        $isBuryadToRussian = true;
        $fromToText.text('бурятско-русский');
        $input.val('');
        $input.attr('placeholder', textBur);
        $("#buryad-letters-wrapper").stop().slideDown(300);
        if (!isDefaultText) {
            $container.stop().slideUp(300, function(){
                $container.text(initialText);
                isDefaultText = true;
                $container.stop().slideDown(300);
            });
        };
    });

    $("#from-rus-to-bur").on('click', function(){
        $(this).addClass('active');
        $("#from-bur-to-rus").removeClass('active');
        $isBuryadToRussian = false;
        $fromToText.text('русско-бурятский');
        $input.val('');
        $input.attr('placeholder', textRus);
        $("#buryad-letters-wrapper").stop().slideUp(300);
        if (!isDefaultText) {
            $container.stop().slideUp(300, function(){
                $container.text(initialText);
                isDefaultText = true;
                $container.stop().slideDown(300);
            });
        };
    });

    $(".buryad-letter").on('click', function(){
        let taken_letter = $(this).text();
        let result_word = $input.val() + taken_letter;
        $input.val(result_word).focus();
    });

    $("#form-input").on('submit', async function(event){
        event.preventDefault();

        try {
            let input_word = $input.val();
            let language = $isBuryadToRussian ? 'buryat-word' : 'russian-word';
            let response = await fetch(`https://burlang.ru/api/v1/${language}/translate?q=${input_word}`);

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error(notFoundText);
                } else {
                    throw new Error(serverErrorText);
                }
            }


            let data = await response.json();
            let translations = data.translations;
            let all_translations = translations.map(item => item.value);

            if (all_translations.length == 0) {
                throw new Error(notFoundText);
            }

            all_translations = all_translations.join('\n');

            isDefaultText = false;
            $container.stop().slideUp(300, function(){
                $container.text(all_translations);
                $container.stop().slideDown(300);
            });
            

        } catch(error) {
            isDefaultText = false;
            $container.stop().slideUp(300, function(){
                $container.text(error.message);
                $container.stop().slideDown(300);
            });
        }
    });

});