from django import forms


class TipTapWidget(forms.Textarea):
    """
    Кастомный виджет для редактирования HTML уроков через современный редактор TipTap.
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'data-tiptap-editor': 'true',
            'class': 'tiptap-editor',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    class Media:
        css = {
            'all': ('courses/css/tiptap.css',)
        }
        js = (
            'courses/js/tiptap.bundle.min.js',
            'courses/js/tiptap-editor.js',
        )
