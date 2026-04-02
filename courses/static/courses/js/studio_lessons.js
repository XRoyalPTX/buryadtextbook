$(document).ready(function(){

    const el = document.getElementById('lesson-sortable-container');
    const url = el.dataset.url
    const token = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const sortable = new Sortable(el, {
        animation: 150,  
        ghostClass: 'blue-background-class',
        handle: '.drag-handle',
        onEnd: function(evt) {
            const formData = new FormData();
            const order = sortable.toArray()

            order.forEach(id => {
                formData.append('order[]', id);
            });

            fetch(url, {
                method: 'POST',
                headers: {
                    "X-CSRFToken": token
                },
                body: formData,
            })
            .then(response => {
                if (response.ok) {
                    console.log("Порядок сохранен");
                } else {
                    alert("Ошибка при сохранении порядка. Статус сервера: " + response.status);
                }
            })
        }
    });

})