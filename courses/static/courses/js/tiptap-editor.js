/**
 * TipTap Editor Controller for Django Forms (BuryadTextbook)
 */
(function() {
    'use strict';

    function initTipTapEditor(textarea) {
        if (textarea.dataset.tiptapInitialized === 'true') {
            return;
        }
        textarea.dataset.tiptapInitialized = 'true';

        // Check if TipTap bundle is loaded
        if (!window.TipTap || !window.TipTap.Editor) {
            console.error('TipTap bundle is not loaded.');
            return;
        }

        const {
            Editor,
            StarterKit,
            Underline,
            Link,
            Highlight,
            Table,
            TableRow,
            TableCell,
            TableHeader
        } = window.TipTap;

        // Hide the original textarea
        textarea.style.display = 'none';

        // Create container structure
        const container = document.createElement('div');
        container.className = 'tiptap-container';

        // 1. Toolbar HTML (Wrapping toolbar with clean visual groups)
        const toolbar = document.createElement('div');
        toolbar.className = 'tiptap-toolbar';
        toolbar.innerHTML = `
            <div class="tiptap-btn-group">
                <button type="button" class="tiptap-btn" data-action="paragraph" title="Обычный текст">¶</button>
                <button type="button" class="tiptap-btn" data-action="h2" title="Заголовок 2">H2</button>
                <button type="button" class="tiptap-btn" data-action="h3" title="Заголовок 3">H3</button>
            </div>
            <div class="tiptap-divider"></div>
            <div class="tiptap-btn-group">
                <button type="button" class="tiptap-btn" data-action="bold" title="Жирный (Ctrl+B)"><b>B</b></button>
                <button type="button" class="tiptap-btn" data-action="italic" title="Курсив (Ctrl+I)"><i>I</i></button>
                <button type="button" class="tiptap-btn" data-action="underline" title="Подчеркнутый (Ctrl+U)"><u>U</u></button>
                <button type="button" class="tiptap-btn" data-action="strike" title="Зачеркнутый"><s>S</s></button>
                <button type="button" class="tiptap-btn" data-action="highlight" title="Выделение маркером">🖌</button>
            </div>
            <div class="tiptap-divider"></div>
            <div class="tiptap-btn-group">
                <button type="button" class="tiptap-btn" data-action="bulletList" title="Маркированный список">• Список</button>
                <button type="button" class="tiptap-btn" data-action="orderedList" title="Нумерованный список">1. Список</button>
                <button type="button" class="tiptap-btn" data-action="hr" title="Разделительная линия">—</button>
            </div>
            <div class="tiptap-divider"></div>
            <div class="tiptap-btn-group">
                <button type="button" class="tiptap-btn" data-action="link" title="Вставить ссылку">🔗 Ссылка</button>
                <button type="button" class="tiptap-btn" data-action="open-table-modal" title="Таблицы">⊞ Таблица</button>
            </div>
            <div class="tiptap-divider"></div>
            <div class="tiptap-btn-group" title="Бурятские буквы (быстрый ввод)">
                <button type="button" class="tiptap-btn tiptap-btn-buryat" data-char="ү">ү</button>
                <button type="button" class="tiptap-btn tiptap-btn-buryat" data-char="ө">ө</button>
                <button type="button" class="tiptap-btn tiptap-btn-buryat" data-char="һ">һ</button>
                <button type="button" class="tiptap-btn tiptap-btn-buryat" data-char="Ү">Ү</button>
                <button type="button" class="tiptap-btn tiptap-btn-buryat" data-char="Ө">Ө</button>
                <button type="button" class="tiptap-btn tiptap-btn-buryat" data-char="Һ">Һ</button>
            </div>
            <div class="tiptap-divider"></div>
            <div class="tiptap-btn-group">
                <button type="button" class="tiptap-btn" data-action="undo" title="Отменить (Ctrl+Z)">↶</button>
                <button type="button" class="tiptap-btn" data-action="redo" title="Повторить (Ctrl+Y)">↷</button>
            </div>
        `;

        // 2. Editor mount element
        const editorMount = document.createElement('div');
        editorMount.className = 'tiptap-editor-content';

        // 3. Footer & Character count
        const footer = document.createElement('div');
        footer.className = 'tiptap-footer';
        footer.innerHTML = `
            <span class="tiptap-status">💡 Бурятские буквы ү, ө, һ доступны для быстрого ввода в панели</span>
            <span class="tiptap-char-count">Символов: <span class="count-value">0</span> / 50 000</span>
        `;

        // Assemble editor container
        container.appendChild(toolbar);
        container.appendChild(editorMount);
        container.appendChild(footer);
        textarea.parentNode.insertBefore(container, textarea.nextSibling);

        // 4. Modal Dialog for Table Actions (Appended to body to float on top of everything)
        let modalBackdrop = document.getElementById('tiptap-table-modal');
        if (!modalBackdrop) {
            modalBackdrop = document.createElement('div');
            modalBackdrop.className = 'tiptap-modal-backdrop';
            modalBackdrop.id = 'tiptap-table-modal';
            modalBackdrop.innerHTML = `
                <div class="tiptap-modal">
                    <div class="tiptap-modal-header">
                        <h4 class="tiptap-modal-title">⊞ Управление таблицей</h4>
                        <button type="button" class="tiptap-modal-close" data-modal-close title="Закрыть">✕</button>
                    </div>
                    <div class="tiptap-modal-body">
                        <div>
                            <button type="button" class="tiptap-modal-btn tiptap-modal-btn-primary" data-action="table-insert">
                                ➕ Вставить таблицу (3×3)
                            </button>
                        </div>
                        <div>
                            <div class="tiptap-modal-section-title">Строки</div>
                            <div class="tiptap-modal-grid">
                                <button type="button" class="tiptap-modal-btn" data-action="table-add-row-after">➕ Добавить строку ниже</button>
                                <button type="button" class="tiptap-modal-btn" data-action="table-delete-row">✕ Удалить строку</button>
                            </div>
                        </div>
                        <div>
                            <div class="tiptap-modal-section-title">Столбцы</div>
                            <div class="tiptap-modal-grid">
                                <button type="button" class="tiptap-modal-btn" data-action="table-add-col-after">➕ Добавить столбец справа</button>
                                <button type="button" class="tiptap-modal-btn" data-action="table-delete-col">✕ Удалить столбец</button>
                            </div>
                        </div>
                        <div>
                            <div class="tiptap-modal-section-title">Опасная зона</div>
                            <button type="button" class="tiptap-modal-btn tiptap-modal-btn-danger" data-action="table-delete">
                                🗑 Удалить всю таблицу
                            </button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modalBackdrop);
        }

        const countValEl = footer.querySelector('.count-value');
        const charCountEl = footer.querySelector('.tiptap-char-count');

        // Initialize TipTap
        const editor = new Editor({
            element: editorMount,
            extensions: [
                StarterKit.configure({
                    heading: {
                        levels: [2, 3]
                    }
                }),
                Underline,
                Highlight.configure({ multicolor: true }),
                Link.configure({
                    openOnClick: false,
                    HTMLAttributes: {
                        target: '_blank',
                        rel: 'noopener noreferrer'
                    }
                }),
                Table.configure({
                    resizable: true
                }),
                TableRow,
                TableHeader,
                TableCell
            ],
            content: textarea.value || '<p></p>',
            onUpdate: ({ editor }) => {
                syncContent(editor);
            },
            onTransaction: () => {
                updateActiveStates();
            }
        });

        function syncContent(ed) {
            const html = ed.getHTML();
            textarea.value = html;

            const textLength = ed.getText().length;
            countValEl.textContent = textLength.toLocaleString();
            if (textLength > 50000) {
                charCountEl.className = 'tiptap-char-count danger';
            } else if (textLength > 45000) {
                charCountEl.className = 'tiptap-char-count warning';
            } else {
                charCountEl.className = 'tiptap-char-count';
            }
        }

        function updateActiveStates() {
            const buttons = container.querySelectorAll('.tiptap-btn[data-action]');
            buttons.forEach(btn => {
                const action = btn.dataset.action;
                let isActive = false;
                switch (action) {
                    case 'bold': isActive = editor.isActive('bold'); break;
                    case 'italic': isActive = editor.isActive('italic'); break;
                    case 'underline': isActive = editor.isActive('underline'); break;
                    case 'strike': isActive = editor.isActive('strike'); break;
                    case 'highlight': isActive = editor.isActive('highlight'); break;
                    case 'h2': isActive = editor.isActive('heading', { level: 2 }); break;
                    case 'h3': isActive = editor.isActive('heading', { level: 3 }); break;
                    case 'paragraph': isActive = editor.isActive('paragraph'); break;
                    case 'bulletList': isActive = editor.isActive('bulletList'); break;
                    case 'orderedList': isActive = editor.isActive('orderedList'); break;
                    case 'blockquote': isActive = editor.isActive('blockquote'); break;
                    case 'link': isActive = editor.isActive('link'); break;
                }
                if (isActive) {
                    btn.classList.add('is-active');
                } else {
                    btn.classList.remove('is-active');
                }
            });
        }

        // Modal Helpers
        function openTableModal() {
            modalBackdrop.classList.add('is-open');
        }

        function closeTableModal() {
            modalBackdrop.classList.remove('is-open');
        }

        // Action dispatcher
        function handleAction(action) {
            switch (action) {
                case 'bold': editor.chain().focus().toggleBold().run(); break;
                case 'italic': editor.chain().focus().toggleItalic().run(); break;
                case 'underline': editor.chain().focus().toggleUnderline().run(); break;
                case 'strike': editor.chain().focus().toggleStrike().run(); break;
                case 'highlight': editor.chain().focus().toggleHighlight().run(); break;
                case 'paragraph': editor.chain().focus().setParagraph().run(); break;
                case 'h2': editor.chain().focus().toggleHeading({ level: 2 }).run(); break;
                case 'h3': editor.chain().focus().toggleHeading({ level: 3 }).run(); break;
                case 'bulletList': editor.chain().focus().toggleBulletList().run(); break;
                case 'orderedList': editor.chain().focus().toggleOrderedList().run(); break;
                case 'blockquote': editor.chain().focus().toggleBlockquote().run(); break;
                case 'hr': editor.chain().focus().setHorizontalRule().run(); break;
                case 'undo': editor.chain().focus().undo().run(); break;
                case 'redo': editor.chain().focus().redo().run(); break;
                case 'link': {
                    if (editor.isActive('link')) {
                        editor.chain().focus().unsetLink().run();
                    } else {
                        const previousUrl = editor.getAttributes('link').href;
                        const url = window.prompt('Введите URL ссылки:', previousUrl || 'https://');
                        if (url) {
                            editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
                        }
                    }
                    break;
                }
                case 'open-table-modal':
                    openTableModal();
                    break;
                case 'table-insert':
                    editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
                    closeTableModal();
                    break;
                case 'table-add-row-after':
                    editor.chain().focus().addRowAfter().run();
                    closeTableModal();
                    break;
                case 'table-delete-row':
                    editor.chain().focus().deleteRow().run();
                    closeTableModal();
                    break;
                case 'table-add-col-after':
                    editor.chain().focus().addColumnAfter().run();
                    closeTableModal();
                    break;
                case 'table-delete-col':
                    editor.chain().focus().deleteColumn().run();
                    closeTableModal();
                    break;
                case 'table-delete':
                    editor.chain().focus().deleteTable().run();
                    closeTableModal();
                    break;
            }
        }

        // Attach clicks to toolbar
        container.addEventListener('click', (e) => {
            const btn = e.target.closest('.tiptap-btn');
            if (!btn) return;

            // Special Buryat Char Buttons
            if (btn.dataset.char) {
                e.preventDefault();
                const char = btn.dataset.char;
                editor.chain().focus().insertContent(char).run();
                return;
            }

            // Action buttons
            if (btn.dataset.action) {
                e.preventDefault();
                handleAction(btn.dataset.action);
            }
        });

        // Attach clicks to table modal
        modalBackdrop.addEventListener('click', (e) => {
            // Close on backdrop click
            if (e.target === modalBackdrop) {
                closeTableModal();
                return;
            }
            // Close button
            if (e.target.closest('[data-modal-close]')) {
                closeTableModal();
                return;
            }
            // Action button inside modal
            const actionBtn = e.target.closest('.tiptap-modal-btn');
            if (actionBtn && actionBtn.dataset.action) {
                e.preventDefault();
                handleAction(actionBtn.dataset.action);
            }
        });

        // Close modal on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modalBackdrop.classList.contains('is-open')) {
                closeTableModal();
            }
        });

        // Sync on form submit as a fail-safe
        const form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                textarea.value = editor.getHTML();
            });
        }

        // Initial sync and count
        syncContent(editor);
        updateActiveStates();
    }

    // Auto-init on DOMContentLoaded
    function autoInit() {
        const textareas = document.querySelectorAll('textarea[data-tiptap-editor="true"], textarea.tiptap-editor');
        textareas.forEach(initTipTapEditor);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoInit);
    } else {
        autoInit();
    }

    // Export globally
    window.initTipTapEditor = initTipTapEditor;
})();
