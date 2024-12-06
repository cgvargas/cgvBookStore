// static/js/csrf-setup.js
$(document).ready(function() {
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    });
});