"""Scripts JS injetados pelo Pythomic no navegador.

Padrão do projeto mantido:
    * THEME_BOOT_SCRIPT — aplica no primeiro carregamento o tema salvo no
      localStorage no <html> e avisa o servidor por um input escondido
      (py_theme_input) via evento "input".
    * _theme_sync_script — aplica e persiste o tema atual; é remontado a
      cada mudança (a key muda junto com o estado), executando de novo.
    * _make_upload_script — o input de arquivo lê o arquivo como data URL
      (base64) e despeja num input escondido, cujo evento "input" chega ao
      servidor. Valida o tamanho (10 MB) no cliente com mensagem em pt-BR
      antes de ler, e trata falhas de leitura. Uma cópia é gerada por par
      de ids (mídia do post e foto de perfil).
"""

THEME_BOOT_SCRIPT = """
(function () {
    // Garante o <meta name="viewport"> no <head>. Sem ele, o celular renderiza
    // a página a ~980px (escala de desktop) e a interface fica minúscula — o
    // tablet, por ter largura próxima a 980px, parece normal, mas o celular
    // não. O run.py já tenta injetar via Options(head=...); este bloco é a
    // garantia independente da versão do ReactPy: cria o meta se faltar, ou
    // reforça o conteúdo correto se já existir. O navegador reflowa em seguida.
    var vp = document.querySelector('meta[name="viewport"]');
    var vpContent = 'width=device-width, initial-scale=1, maximum-scale=5, viewport-fit=cover';
    if (!vp) {
        vp = document.createElement('meta');
        vp.name = 'viewport';
        document.head.appendChild(vp);
    }
    vp.setAttribute('content', vpContent);

    var tema = 'light';
    try { tema = localStorage.getItem('pythomic_theme') || 'light'; } catch (err) { tema = 'light'; }
    if (tema !== 'dark') { tema = 'light'; }
    document.documentElement.dataset.theme = tema;
    setTimeout(function () {
        var input = document.getElementById('py_theme_input');
        if (!input) return;
        input.value = tema;
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }, 0);
})();
"""


def _theme_sync_script(is_dark: bool) -> str:
    """Script que aplica e persiste o tema atual no <html> + localStorage.

    É remontado a cada mudança de tema (a key muda junto com o estado),
    executando novamente e gravando a escolha do usuário.
    """
    tema = "dark" if is_dark else "light"
    return (
        "(function () {\n"
        "    document.documentElement.dataset.theme = '" + tema + "';\n"
        "    try { localStorage.setItem('pythomic_theme', '" + tema + "'); } catch (err) {}\n"
        "})();"
    )


def _make_upload_script(file_input_id: str, hidden_input_id: str) -> str:
    """Gera o script de upload para um par (input de arquivo, input escondido)."""
    return """
(function () {
    var fileInput = document.getElementById('FILE_INPUT_ID');
    if (!fileInput || fileInput.dataset.pyBound) return;
    fileInput.dataset.pyBound = '1';
    fileInput.addEventListener('change', function (e) {
        var file = e.target.files[0];
        if (!file) return;
        var LIMITE = 10 * 1024 * 1024;
        if (file.size > LIMITE) {
            alert('Arquivo muito grande. O tamanho máximo permitido é 10 MB.');
            e.target.value = '';
            return;
        }
        var reader = new FileReader();
        reader.onload = function (ev) {
            var hidden = document.getElementById('HIDDEN_INPUT_ID');
            if (!hidden) return;
            hidden.value = ev.target.result;
            hidden.dispatchEvent(new Event('input', { bubbles: true }));
        };
        reader.onerror = function () {
            alert('Não foi possível ler o arquivo. Tente novamente.');
        };
        reader.readAsDataURL(file);
    });
})();
""".replace("FILE_INPUT_ID", file_input_id).replace("HIDDEN_INPUT_ID", hidden_input_id)


# Upload de mídia dos posts (ids originais preservados).
FILE_UPLOAD_SCRIPT = _make_upload_script("py_file_input", "py_base64_input")

# Upload da foto de perfil (ids próprios, sem colidir com o modal de post).
AVATAR_UPLOAD_SCRIPT = _make_upload_script("py_avatar_file_input", "py_avatar_b64_input")
