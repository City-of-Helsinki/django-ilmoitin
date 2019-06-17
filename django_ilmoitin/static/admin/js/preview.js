function showPreviewModal() {
    django.jQuery.post(
        '',
        django.jQuery('#notificationtemplate_form').serialize() + '&_preview',
        function (html) {
            var w = window.open('about:blank', 'preview', 'width=800,height=800,resizeable,scrollbars,directories=no,titlebar=no,toolbar=no,location=no,status=no,menubar=no');
            w.document.open();
            w.document.write(html);
            w.document.close();
            w.document.title = "Preview template"
        }
    )
}
