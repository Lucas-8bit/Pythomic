"""CSS global do Pythomic (versão 3.0 — redesign ENORME, mobile-only, animado).

Correções principais em relação à v2:
    * BUG CRÍTICO CORRIGIDO: o shell padrão do ReactPy não tem <meta viewport>,
      então no celular a página renderizava a ~980px (escala de desktop) e ficava
      "bugada". Agora o run.py injeta o viewport via Options(head=...) e este CSS
      é todo construído em vw/clamp() para a tela real do dispositivo.

Expandido para "extremamente detalhado com muitas animações e muitos efeitos":
    * Fundo em MESH GRADIENTE ANIMADO (blobs flutuantes em camadas).
    * GLASSMORPHISM em cabeçalho, nav inferior, cards e modais.
    * LOGO com gradiente animado + brilho pulsante + flutuação.
    * WELCOME: aurora gradiente, partículas flutuantes, CTA com shimmer,
      cards de diferenciais com entrada escalonada e elevação no hover.
    * FEED: entrada escalonada dos cards, elevação no hover, anel do avatar
      com gradiente girando, mídia com Ken Burns sutil no hover.
    * CURTIR: heart pop + BURST de partículas (CSS puro) + contagem com pop.
    * NAV INFERIOR: indicador deslizante + ícone com bounce.
    * FAB (botão flutuante de criar post) com pulso + gradiente animado.
    * MODAIS (top sheets): descem do topo com bounce, overlay com blur,
      conteúdo com entrada escalonada.
    * RIPPLE nos botões, feedback de toque (scale) em tudo, foco com glow.
    * SKELETON shimmer, spinner, transições suaves de tema.
    * ADAPTATIVO: coluna única em todos os tamanhos (mobile-only, sem mais
      feed em 2 colunas).
    * Acessibilidade: @media (prefers-reduced-motion: reduce) desativa tudo.
"""

GLOBAL_CSS = r"""
/* ============================================================
   1. TOKENS DE DESIGN
   ============================================================ */
:root {
    /* Paleta — light */
    --bg: #f4f5fb;
    --bg-grad-1: #eef1ff;
    --bg-grad-2: #fdeef6;
    --bg-grad-3: #e8fbff;
    --card: #ffffff;
    --card-glass: rgba(255, 255, 255, 0.74);
    --card-glass-strong: rgba(255, 255, 255, 0.92);
    --text: #0f1222;
    --text-soft: #3a3f55;
    --muted: #8a8fa3;
    --border: #e7e8f0;
    --border-soft: #f0f1f7;
    --input-bg: #f3f4fa;
    --brand: #5b5bf6;
    --brand-2: #d629a5;
    --brand-3: #f58529;
    --brand-grad: linear-gradient(135deg, #f58529 0%, #d629a5 48%, #5b5bf6 100%);
    --brand-grad-soft: linear-gradient(135deg, rgba(245,133,41,.12), rgba(214,41,165,.12), rgba(91,91,246,.12));
    --brand-grad-glow: linear-gradient(135deg, rgba(245,133,41,.35), rgba(214,41,165,.35), rgba(91,91,246,.35));
    --danger: #ef4458;
    --danger-grad: linear-gradient(135deg, #ff6b6b, #ef4458);
    --success: #18a957;
    --like: #ff3b5c;
    --shadow-sm: 0 2px 10px rgba(20, 23, 51, 0.07);
    --shadow-md: 0 10px 28px rgba(20, 23, 51, 0.12);
    --shadow-lg: 0 22px 56px rgba(20, 23, 51, 0.18);
    --shadow-brand: 0 12px 30px rgba(91, 91, 246, 0.32);
    --shadow-pink: 0 12px 30px rgba(214, 41, 165, 0.30);
    --radius-xs: 8px;
    --radius-sm: 12px;
    --radius: 18px;
    --radius-lg: 24px;
    --radius-xl: 30px;
    --ease: cubic-bezier(0.4, 0, 0.2, 1);
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
    --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
    --nav-h: 66px;
    --header-h: 60px;
    --safe-top: env(safe-area-inset-top, 0px);
    --safe-bottom: env(safe-area-inset-bottom, 0px);
}
html[data-theme="dark"] {
    --bg: #05060c;
    --bg-grad-1: #0b0d1c;
    --bg-grad-2: #160a18;
    --bg-grad-3: #08121a;
    --card: #11131f;
    --card-glass: rgba(17, 19, 31, 0.72);
    --card-glass-strong: rgba(17, 19, 31, 0.92);
    --text: #f3f4fb;
    --text-soft: #c8ccdb;
    --muted: #9aa0b8;
    --border: #232637;
    --border-soft: #1a1c2b;
    --input-bg: #161827;
    --brand-grad-soft: linear-gradient(135deg, rgba(245,133,41,.16), rgba(214,41,165,.16), rgba(91,91,246,.16));
    --brand-grad-glow: linear-gradient(135deg, rgba(245,133,41,.45), rgba(214,41,165,.45), rgba(91,91,246,.45));
    --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.45);
    --shadow-md: 0 10px 28px rgba(0, 0, 0, 0.55);
    --shadow-lg: 0 22px 56px rgba(0, 0, 0, 0.65);
    --shadow-brand: 0 12px 30px rgba(91, 91, 246, 0.45);
    --shadow-pink: 0 12px 30px rgba(214, 41, 165, 0.40);
}

/* ============================================================
   2. RESET + BASE + FUNDO MESH GRADIENTE ANIMADO
   ============================================================ */
*, *::before, *::after { box-sizing: border-box; }
html, body { height: 100%; }
html { -webkit-text-size-adjust: 100%; }

body {
    margin: 0;
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
    background: var(--bg);
    overflow-x: hidden;
    overscroll-behavior-y: none;
    transition: background 0.5s var(--ease), color 0.35s var(--ease);
}

/* Camada 0 do fundo: gradiente radial estático */
body::before {
    content: "";
    position: fixed;
    inset: -20%;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(45% 35% at 12% 8%, var(--bg-grad-2) 0%, transparent 60%),
        radial-gradient(40% 32% at 88% 6%, var(--bg-grad-1) 0%, transparent 60%),
        radial-gradient(50% 40% at 80% 92%, var(--bg-grad-3) 0%, transparent 60%),
        radial-gradient(45% 35% at 8% 88%, var(--bg-grad-1) 0%, transparent 60%);
    animation: pythomic-mesh 18s var(--ease) infinite alternate;
}
/* Camada 1 do fundo: blobs grandes flutuantes (glass colorido) */
body::after {
    content: "";
    position: fixed;
    inset: -30%;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(circle at 30% 30%, rgba(214, 41, 165, 0.10), transparent 22%),
        radial-gradient(circle at 70% 60%, rgba(91, 91, 246, 0.12), transparent 24%),
        radial-gradient(circle at 50% 80%, rgba(245, 133, 41, 0.08), transparent 22%);
    filter: blur(40px);
    animation: pythomic-blobs 22s var(--ease) infinite alternate;
}
html[data-theme="dark"] body::after {
    background:
        radial-gradient(circle at 30% 30%, rgba(214, 41, 165, 0.18), transparent 22%),
        radial-gradient(circle at 70% 60%, rgba(91, 91, 246, 0.20), transparent 24%),
        radial-gradient(circle at 50% 80%, rgba(245, 133, 41, 0.12), transparent 22%);
}
@keyframes pythomic-mesh {
    0%   { transform: translate(0, 0) scale(1); }
    100% { transform: translate(-3%, 2%) scale(1.06); }
}
@keyframes pythomic-blobs {
    0%   { transform: translate(0, 0) rotate(0deg); }
    100% { transform: translate(4%, -3%) rotate(8deg); }
}

button, input, textarea, select { font-family: inherit; font-size: 16px; }
a { color: var(--brand); text-decoration: none; }
img { display: block; max-width: 100%; }
::-webkit-scrollbar { width: 0; height: 0; }
:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }

/* Shell: acima do fundo, com fade-in a cada montagem de tela.
   IMPORTANTE: NÃO usar transform aqui (nem em nenhum ancestral de elementos
   position: fixed). Um transform retido (animation-fill-mode: both) cria um
   containing block para os descendentes fixed, fazendo a nav inferior, o FAB
   e os modais serem posicionados relativos a .py-shell em vez da viewport —
   era exatamente isso que deixava o layout "bugado". Usamos só opacity. */
.py-shell {
    position: relative;
    z-index: 1;
    animation: pythomic-fade 0.5s var(--ease-out) both;
}
@keyframes pythomic-fade {
    from { opacity: 0; }
    to   { opacity: 1; }
}
/* fade-up: usado em elementos que NÃO contêm descendentes position: fixed
   (textos, cards de boas-vindas, títulos de modal, etc.). Nunca usar em
   .py-shell ou em qualquer ancestral de elementos fixed. */
@keyframes pythomic-fade-up {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ============================================================
   3. LOGO — gradiente animado + brilho + flutuação
   ============================================================ */
.py-logo {
    font-family: "Brush Script MT", "Segoe Script", "Lucida Handwriting",
        "Snell Roundhand", cursive;
    font-weight: bold;
    background: var(--brand-grad);
    background-size: 220% 220%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
    letter-spacing: 0.5px;
    animation: pythomic-logo-grad 6s var(--ease) infinite,
               pythomic-float 4s var(--ease) infinite;
    filter: drop-shadow(0 6px 18px rgba(214, 41, 165, 0.28));
}
@keyframes pythomic-logo-grad {
    0%, 100% { background-position: 0% 50%; }
    50%      { background-position: 100% 50%; }
}
@keyframes pythomic-float {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-5px); }
}

/* ============================================================
   4. BOAS-VINDAS — aurora, partículas, hero, CTA shimmer, features
   ============================================================ */
.py-welcome {
    position: relative;
    min-height: 100vh;
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: calc(32px + var(--safe-top)) 24px calc(32px + var(--safe-bottom));
    text-align: center;
    gap: 6px;
    overflow: hidden;
}
/* Aurora atrás do hero */
.py-welcome::before {
    content: "";
    position: absolute;
    inset: -10%;
    z-index: -1;
    background: var(--brand-grad);
    background-size: 300% 300%;
    filter: blur(70px);
    opacity: 0.16;
    animation: pythomic-logo-grad 12s var(--ease) infinite,
               pythomic-blobs 20s var(--ease) infinite alternate;
    border-radius: 50%;
}
/* Partículas flutuantes (3 pontos animados) */
.py-welcome::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -1;
    background-image:
        radial-gradient(circle, rgba(255,255,255,0.9) 1.5px, transparent 2px),
        radial-gradient(circle, rgba(214,41,165,0.7) 1.5px, transparent 2px),
        radial-gradient(circle, rgba(91,91,246,0.7) 1.5px, transparent 2px);
    background-size: 120px 120px, 180px 180px, 220px 220px;
    background-position: 20px 30px, 80px 120px, 150px 60px;
    opacity: 0.5;
    animation: pythomic-particles 30s linear infinite;
}
html[data-theme="dark"] .py-welcome::after { opacity: 0.4; }
@keyframes pythomic-particles {
    from { background-position: 20px 30px, 80px 120px, 150px 60px; }
    to   { background-position: 20px 130px, 80px -60px, 150px 260px; }
}

.py-hero-logo {
    font-size: clamp(54px, 19vw, 96px);
    margin: 0;
    animation: pythomic-hero-in 0.8s var(--ease-spring) both,
               pythomic-logo-grad 6s var(--ease) infinite,
               pythomic-float 4.5s var(--ease) infinite;
}
@keyframes pythomic-hero-in {
    0%   { opacity: 0; transform: scale(0.6) translateY(20px); filter: blur(8px); }
    60%  { opacity: 1; transform: scale(1.08) translateY(0); filter: blur(0); }
    100% { transform: scale(1); }
}
.py-tagline {
    color: var(--text-soft);
    margin: 14px 0 38px;
    font-size: clamp(15px, 4.6vw, 19px);
    font-weight: 500;
    animation: pythomic-fade-up 0.7s var(--ease-out) 0.15s both;
}
.py-cta {
    width: 100%;
    max-width: 340px;
    padding: 17px;
    font-size: clamp(15px, 4.6vw, 17px);
    border-radius: var(--radius);
    animation: pythomic-fade-up 0.8s var(--ease-out) 0.25s both;
}
.py-features {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 42px;
    width: 100%;
    max-width: 360px;
}
.py-feature {
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: clamp(12px, 3.7vw, 14px);
    font-weight: 500;
    color: var(--text-soft);
    background: var(--card-glass);
    backdrop-filter: saturate(180%) blur(14px);
    -webkit-backdrop-filter: saturate(180%) blur(14px);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 15px 17px;
    text-align: left;
    box-shadow: var(--shadow-sm);
    animation: pythomic-feature-in 0.6s var(--ease-out) both;
    transition: transform 0.25s var(--ease-bounce), box-shadow 0.25s var(--ease),
                border-color 0.25s var(--ease);
}
.py-feature:hover {
    transform: translateY(-3px) translateX(2px);
    box-shadow: var(--shadow-md);
    border-color: var(--brand);
}
.py-feature:active { transform: scale(0.98); }
.py-feature:nth-child(1) { animation-delay: 0.35s; }
.py-feature:nth-child(2) { animation-delay: 0.45s; }
.py-feature:nth-child(3) { animation-delay: 0.55s; }
@keyframes pythomic-feature-in {
    from { opacity: 0; transform: translateY(16px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
.py-feature svg {
    flex-shrink: 0;
    color: var(--brand);
    padding: 7px;
    border-radius: var(--radius-sm);
    background: var(--brand-grad-soft);
    transition: transform 0.3s var(--ease-bounce);
}
.py-feature:hover svg { transform: rotate(-8deg) scale(1.1); }

/* ============================================================
   5. AUTENTICAÇÃO — card glass, inputs com glow, toggle
   ============================================================ */
.py-auth {
    position: relative;
    min-height: 100vh;
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-width: 440px;
    margin: 0 auto;
    padding: calc(28px + var(--safe-top)) 24px calc(32px + var(--safe-bottom));
    animation: pythomic-fade-up 0.5s var(--ease-out) both;
}
.py-auth-logo {
    font-size: clamp(42px, 13vw, 58px);
    text-align: center;
    animation: pythomic-hero-in 0.7s var(--ease-spring) both,
               pythomic-logo-grad 6s var(--ease) infinite,
               pythomic-float 4.5s var(--ease) infinite;
}
.py-auth-title {
    margin: 10px 0 22px;
    text-align: center;
    font-size: clamp(17px, 5vw, 21px);
    font-weight: 700;
    animation: pythomic-fade-up 0.6s var(--ease-out) 0.1s both;
}
.py-hint {
    font-size: 12px;
    color: var(--muted);
    margin: 0 0 10px;
    text-align: center;
}
.py-pwd-row { position: relative; margin-bottom: 11px; }
.py-pwd-row .py-input { margin-bottom: 0; padding-right: 48px; }
/* Botão do olhinho DENTRO do campo de senha, no canto direito, centralizado.
   O seletor .py-pwd-row .py-pwd-toggle (especificidade 0,2,0) vence o
   position: relative do .py-icon-btn (0,1,0, definido depois) — sem isso o
   olhinho ficava ao lado do input em vez de sobreposto no canto. */
.py-pwd-row .py-pwd-toggle {
    position: absolute;
    right: 6px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--muted);
    padding: 8px;
    z-index: 2;
    transition: color 0.2s var(--ease), transform 0.2s var(--ease-bounce);
}
.py-pwd-row .py-pwd-toggle:hover { color: var(--brand); transform: translateY(-50%) rotate(10deg); }
.py-pwd-row .py-pwd-toggle:active { transform: translateY(-50%) scale(0.85); }

/* Link de texto (ex.: "Esqueci minha senha") — discreto, cor da marca. */
.py-link {
    background: none;
    border: none;
    color: var(--brand);
    font-size: 13px;
    padding: 4px;
    margin-top: 2px;
    cursor: pointer;
    text-decoration: underline;
    text-underline-offset: 3px;
}
.py-link:hover { opacity: 0.8; }

/* Subtítulo explicativo nas telas de verificação de email / recuperação. */
.py-auth-subtitle {
    margin: 0 0 16px;
    text-align: center;
    font-size: 13px;
    line-height: 1.5;
    color: var(--muted);
}

/* Campo do código de verificação: grande, centralizado, espaçado. */
.py-code-input {
    text-align: center;
    font-size: clamp(20px, 6vw, 26px);
    letter-spacing: 10px;
    font-weight: 700;
    padding-left: 10px;
}

/* ============================================================
   6. FORMULÁRIOS — inputs, textarea, file, error shake, success
   ============================================================ */
.py-input {
    width: 100%;
    padding: 15px 16px;
    margin-bottom: 11px;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--input-bg);
    color: var(--text);
    font-size: 16px;
    outline: none;
    transition: border-color 0.2s var(--ease), box-shadow 0.25s var(--ease),
                background 0.2s var(--ease), transform 0.15s var(--ease);
}
.py-input::placeholder { color: var(--muted); }
.py-input:focus {
    border-color: var(--brand);
    box-shadow: 0 0 0 4px rgba(91, 91, 246, 0.20);
    background: var(--card);
    transform: translateY(-1px);
}
.py-input:hover:not(:focus) { border-color: var(--muted); }
.py-textarea { min-height: 100px; resize: vertical; line-height: 1.5; }
.py-file {
    padding: 11px;
    font-size: 13px;
    cursor: pointer;
}
.py-file:hover { border-color: var(--brand); }
.py-error {
    color: var(--danger);
    background: rgba(239, 68, 88, 0.12);
    border: 1px solid rgba(239, 68, 88, 0.32);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    font-size: 13px;
    font-weight: 600;
    margin: 4px 0 11px;
    text-align: center;
    animation: pythomic-shake 0.5s var(--ease);
}
.py-success {
    color: var(--success);
    background: rgba(24, 169, 87, 0.12);
    border: 1px solid rgba(24, 169, 87, 0.32);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    font-size: 13px;
    font-weight: 600;
    margin: 4px 0 11px;
    text-align: center;
    animation: pythomic-pop-in 0.4s var(--ease-bounce);
}
@keyframes pythomic-shake {
    0%, 100% { transform: translateX(0); }
    15% { transform: translateX(-7px); }
    30% { transform: translateX(7px); }
    45% { transform: translateX(-5px); }
    60% { transform: translateX(5px); }
    75% { transform: translateX(-3px); }
}
@keyframes pythomic-pop-in {
    0%   { opacity: 0; transform: scale(0.85); }
    60%  { transform: scale(1.04); }
    100% { opacity: 1; transform: scale(1); }
}

/* ============================================================
   7. BOTÕES — gradiente animado, shimmer sweep, ripple
   ============================================================ */
.py-btn {
    position: relative;
    overflow: hidden;
    border: none;
    border-radius: var(--radius-sm);
    padding: 15px 18px;
    font-weight: 700;
    font-size: 15px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: transform 0.15s var(--ease), filter 0.18s var(--ease),
                background 0.3s var(--ease), color 0.3s var(--ease),
                border-color 0.3s var(--ease), box-shadow 0.3s var(--ease);
}
.py-btn:active { transform: scale(0.965); }
.py-btn:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }
/* Ripple: pseudo-elemento cresce a partir do centro ao tocar */
.py-btn::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, rgba(255,255,255,0.55) 0%, transparent 60%);
    opacity: 0;
    transform: scale(0.3);
    transition: opacity 0.5s var(--ease), transform 0.5s var(--ease);
    pointer-events: none;
}
.py-btn:active::after { opacity: 1; transform: scale(1.4); transition: 0s; }

.py-btn-primary {
    background: var(--brand-grad);
    background-size: 200% 200%;
    color: #ffffff;
    width: 100%;
    box-shadow: var(--shadow-brand);
    animation: pythomic-btn-grad 5s var(--ease) infinite;
}
.py-btn-primary::before {
    /* Shimmer sweep que percorre o botão */
    content: "";
    position: absolute;
    top: 0; left: -120%;
    width: 80%; height: 100%;
    background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.45) 50%, transparent 100%);
    transform: skewX(-20deg);
    animation: pythomic-shimmer-sweep 3.2s var(--ease) infinite;
    pointer-events: none;
}
@keyframes pythomic-shimmer-sweep {
    0%   { left: -120%; }
    55%, 100% { left: 130%; }
}
@keyframes pythomic-btn-grad {
    0%, 100% { background-position: 0% 50%; }
    50%      { background-position: 100% 50%; }
}
.py-btn-primary:hover { filter: brightness(1.07); transform: translateY(-2px); box-shadow: var(--shadow-pink); }

.py-btn-ghost {
    background: transparent;
    color: var(--brand);
    width: 100%;
    padding: 13px;
    margin-top: 8px;
}
.py-btn-ghost:hover { color: var(--text); background: var(--brand-grad-soft); transform: translateY(-1px); }

.py-btn-outline {
    background: transparent;
    border: 1.5px solid var(--border);
    color: var(--text);
    width: 100%;
}
.py-btn-outline:hover { border-color: var(--brand); color: var(--brand); background: var(--brand-grad-soft); transform: translateY(-1px); }

.py-btn-danger {
    background: transparent;
    border: 1.5px solid var(--danger);
    color: var(--danger);
    width: 100%;
    margin-top: 14px;
}
.py-btn-danger:hover { background: rgba(239, 68, 88, 0.12); transform: translateY(-1px); }

/* Zona de perigo: painel de confirmação da exclusão de conta. */
.py-confirm-box {
    margin-top: 14px;
    padding: 16px;
    border-radius: var(--radius-sm);
    display: flex;
    flex-direction: column;
    gap: 8px;
    animation: pythomic-fade-up 0.3s var(--ease-out) both;
}
.py-danger-zone {
    border: 1.5px solid var(--danger);
    background: rgba(239, 68, 88, 0.06);
}
.py-danger-zone .py-btn { margin-top: 4px; }

/* Botão Excluir (slot do cabeçalho do card, nos posts do próprio usuário).
   Contorno discreto no estado normal; preenchido ao armar a confirmação. */
.py-btn-delete {
    padding: 8px 16px;
    font-size: 13px;
    border-radius: 12px;
    border: 1.5px solid var(--danger);
    background: transparent;
    color: var(--danger);
    font-weight: 700;
    cursor: pointer;
    flex-shrink: 0;
    transition: transform 0.15s var(--ease), background 0.2s var(--ease),
                color 0.2s var(--ease), border-color 0.2s var(--ease);
}
.py-btn-delete:hover { background: rgba(239, 68, 88, 0.12); }
.py-btn-delete:active { transform: scale(0.92); }
.py-btn-delete-confirm {
    background: var(--danger);
    color: #ffffff;
    border-color: var(--danger);
    box-shadow: 0 8px 20px rgba(239, 68, 72, 0.35);
    animation: pythomic-pop-in 0.25s var(--ease-bounce);
}

.py-btn-follow {
    position: relative;
    overflow: hidden;
    padding: 8px 20px;
    font-size: 13px;
    border-radius: 12px;
    border: none;
    font-weight: 700;
    cursor: pointer;
    background: var(--brand-grad);
    background-size: 200% 200%;
    color: #ffffff;
    transition: transform 0.15s var(--ease), filter 0.18s var(--ease), background 0.3s var(--ease);
    flex-shrink: 0;
    box-shadow: var(--shadow-brand);
    animation: pythomic-btn-grad 5s var(--ease) infinite;
}
.py-btn-follow:hover { filter: brightness(1.07); }
.py-btn-follow:active { transform: scale(0.92); }
.py-btn-following {
    background: transparent;
    border: 1.5px solid var(--border);
    color: var(--text);
    box-shadow: none;
    animation: none;
}
.py-btn-following:hover { border-color: var(--muted); background: var(--input-bg); }

.py-icon-btn {
    position: relative;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 9px;
    border-radius: 12px;
    transition: background 0.2s var(--ease), transform 0.2s var(--ease-bounce), color 0.2s var(--ease);
}
.py-icon-btn:hover { background: var(--brand-grad-soft); color: var(--brand); transform: translateY(-1px); }
.py-icon-btn:active { transform: scale(0.88); }
html[data-theme="dark"] .py-icon-btn:hover { background: rgba(255, 255, 255, 0.08); }

/* ============================================================
   8. CABEÇALHO + NAV INFERIOR (glassmorphism)
   ============================================================ */
.py-header {
    position: sticky;
    top: 0;
    z-index: 40;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    padding-top: calc(12px + var(--safe-top));
    background: var(--card-glass);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid var(--border);
    animation: pythomic-slide-down 0.45s var(--ease-out) both;
}
@keyframes pythomic-slide-down {
    from { opacity: 0; transform: translateY(-100%); }
    to   { opacity: 1; transform: translateY(0); }
}
.py-header-logo { font-size: clamp(26px, 7.5vw, 31px); }

.py-tabs {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 50;
    display: flex;
    background: var(--card-glass);
    backdrop-filter: saturate(180%) blur(22px);
    -webkit-backdrop-filter: saturate(180%) blur(22px);
    border-top: 1px solid var(--border);
    padding-bottom: var(--safe-bottom);
    box-shadow: 0 -8px 24px rgba(20, 23, 51, 0.08);
    animation: pythomic-slide-up-in 0.5s var(--ease-out) both;
}
@keyframes pythomic-slide-up-in {
    from { opacity: 0; transform: translateY(100%); }
    to   { opacity: 1; transform: translateY(0); }
}
.py-tab {
    flex: 1;
    background: none;
    border: none;
    padding: 10px 0 12px;
    color: var(--muted);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    position: relative;
    transition: color 0.2s var(--ease), transform 0.2s var(--ease-bounce);
}
.py-tab span { transition: transform 0.25s var(--ease-bounce); }
.py-tab:active { transform: scale(0.9); }
.py-tab:hover { color: var(--text); }
.py-tab:hover svg { transform: translateY(-3px) scale(1.1); }
.py-tab:active svg { animation: pythomic-bounce 0.4s var(--ease-bounce); }
@keyframes pythomic-bounce {
    0%, 100% { transform: translateY(0) scale(1); }
    40% { transform: translateY(-6px) scale(1.15); }
    70% { transform: translateY(0) scale(0.95); }
}
/* Indicador deslizante no topo da aba ativa (aparece ao tocar) */
.py-tab::before {
    content: "";
    position: absolute;
    top: 0;
    width: 28px;
    height: 3px;
    border-radius: 0 0 4px 4px;
    background: var(--brand-grad);
    transform: scaleX(0);
    transition: transform 0.35s var(--ease-bounce);
}
.py-tab:active::before { transform: scaleX(1); }

/* Sidebar de desktop: REMOVIDA (mobile-only). */
.py-sidebar { display: none !important; }

/* ============================================================
   9. FEED — refresh, cards, avatar, mídia, curtir, empty
   ============================================================ */
.py-main {
    max-width: 560px;
    margin: 0 auto;
    /* Sem barra inferior: só uma folga embaixo (+ safe-area) para o último
       card não colar no fim da tela. */
    padding: 0 0 calc(28px + var(--safe-bottom));
}
.py-feed-top { padding: 16px 14px 0; }
.py-refresh {
    position: relative;
    overflow: hidden;
    width: 100%;
    padding: 13px;
    border: 1.5px solid var(--border);
    background: var(--card-glass);
    backdrop-filter: saturate(180%) blur(12px);
    -webkit-backdrop-filter: saturate(180%) blur(12px);
    color: var(--text);
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-weight: 700;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: var(--shadow-sm);
    transition: border-color 0.2s var(--ease), color 0.2s var(--ease),
                transform 0.15s var(--ease), box-shadow 0.25s var(--ease);
}
.py-refresh:hover { border-color: var(--brand); color: var(--brand); transform: translateY(-1px); box-shadow: var(--shadow-md); }
.py-refresh:active { transform: scale(0.985); }
.py-refresh:active svg { animation: pythomic-spin 0.7s var(--ease); }
@keyframes pythomic-spin { to { transform: rotate(360deg); } }

.py-card {
    position: relative;
    background: var(--card-glass-strong);
    backdrop-filter: saturate(180%) blur(16px);
    -webkit-backdrop-filter: saturate(180%) blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    overflow: hidden;
    margin: 18px 14px 0;
    animation: pythomic-card-in 0.55s var(--ease-out) both;
    transition: transform 0.3s var(--ease-bounce), box-shadow 0.3s var(--ease),
                border-color 0.3s var(--ease);
}
.py-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--brand);
}
/* Borda gradiente sutil no topo do card */
.py-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--brand-grad);
    background-size: 200% 200%;
    opacity: 0;
    transition: opacity 0.3s var(--ease);
    animation: pythomic-btn-grad 5s var(--ease) infinite;
}
.py-card:hover::before { opacity: 0.85; }
/* Entrada escalonada */
.py-card:nth-child(1) { animation-delay: 0.02s; }
.py-card:nth-child(2) { animation-delay: 0.08s; }
.py-card:nth-child(3) { animation-delay: 0.14s; }
.py-card:nth-child(4) { animation-delay: 0.20s; }
.py-card:nth-child(5) { animation-delay: 0.26s; }
.py-card:nth-child(6) { animation-delay: 0.32s; }
.py-card:nth-child(7) { animation-delay: 0.38s; }
.py-card:nth-child(8) { animation-delay: 0.44s; }
@keyframes pythomic-card-in {
    from { opacity: 0; transform: translateY(22px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

.py-post-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 13px 14px;
}
.py-post-user {
    display: flex;
    align-items: center;
    gap: 11px;
    min-width: 0;
    cursor: pointer;
    transition: opacity 0.15s var(--ease), transform 0.2s var(--ease-bounce);
}
.py-post-user:hover { transform: translateX(2px); }
.py-post-user:active { opacity: 0.6; transform: scale(0.98); }

/* Avatar com ANEL DE GRADIENTE GIRANDO (estilo stories) */
.py-avatar {
    position: relative;
    width: 46px;
    height: 46px;
    border-radius: 50%;
    padding: 2.5px;
    background: var(--brand-grad);
    background-size: 200% 200%;
    flex-shrink: 0;
    animation: pythomic-logo-grad 7s var(--ease) infinite;
    transition: transform 0.3s var(--ease-bounce);
}
.py-avatar:hover { transform: scale(1.08) rotate(-4deg); }
.py-avatar img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
    border: 2.5px solid var(--card);
    display: block;
    background: var(--input-bg);
}
.py-avatar-sm { width: 38px; height: 38px; }
.py-avatar-lg { width: 96px; height: 96px; }

.py-user-name {
    font-weight: 700;
    font-size: 14px;
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.py-user-meta { font-size: 12px; color: var(--muted); }

.py-media {
    width: 100%;
    display: block;
    max-height: 640px;
    object-fit: cover;
    background: #000;
    animation: pythomic-fade 0.5s var(--ease) both;
    transition: transform 6s var(--ease-out);
}
.py-card:hover .py-media { transform: scale(1.04); } /* Ken Burns sutil */
@keyframes pythomic-fade {
    from { opacity: 0; }
    to   { opacity: 1; }
}

.py-post-actions {
    padding: 10px 12px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Botão curtir: heart pop + BURST de partículas ao tocar */
.py-like-btn {
    position: relative;
    background: none;
    border: none;
    padding: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    border-radius: 10px;
    color: var(--muted);
    transition: background 0.15s var(--ease), transform 0.2s var(--ease-bounce), color 0.2s var(--ease);
}
.py-like-btn:hover { background: rgba(239, 68, 72, 0.12); color: var(--like); }
.py-like-btn:active { transform: scale(0.82); }
html[data-theme="dark"] .py-like-btn:hover { background: rgba(255, 255, 255, 0.08); }
/* Burst: 4 partículas em cruz que se dissipam ao "pop" */
.py-pop { display: inline-flex; position: relative; animation: pythomic-heart-pop 0.5s var(--ease); }
.py-pop::before, .py-pop::after,
.py-pop > span::before, .py-pop > span::after {
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--like);
    opacity: 0;
}
.py-pop::before { animation: pythomic-burst 0.5s var(--ease) forwards; --bx: 14px; --by: 0; }
.py-pop::after  { animation: pythomic-burst 0.5s var(--ease) forwards; --bx: -14px; --by: 0; }
.py-pop > span::before { animation: pythomic-burst 0.5s var(--ease) forwards; --bx: 0; --by: -14px; }
.py-pop > span::after  { animation: pythomic-burst 0.5s var(--ease) forwards; --bx: 0; --by: 14px; }
@keyframes pythomic-heart-pop {
    0%   { transform: scale(1); }
    30%  { transform: scale(1.55); filter: drop-shadow(0 0 0 rgba(255,59,92,0)); }
    55%  { transform: scale(0.88); }
    100% { transform: scale(1); filter: drop-shadow(0 0 10px rgba(255,59,92,0.55)); }
}
@keyframes pythomic-burst {
    0%   { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    100% { opacity: 0; transform: translate(calc(-50% + var(--bx)), calc(-50% + var(--by))) scale(0.3); }
}

.py-likes {
    font-weight: 700;
    font-size: 14px;
    color: var(--text);
    transition: transform 0.25s var(--ease-bounce);
    animation: pythomic-pop-in 0.3s var(--ease-bounce);
}
.py-caption {
    margin: 8px 14px 16px;
    font-size: 14px;
    line-height: 1.55;
    color: var(--text);
    word-wrap: break-word;
}
.py-caption strong { margin-right: 6px; }

.py-views {
    margin-left: auto;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 13px;
    font-weight: 600;
    color: var(--muted);
}
.py-views svg { animation: pythomic-pulse 2.5s var(--ease) infinite; }
@keyframes pythomic-pulse {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.45; }
}

.py-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 84px 24px;
    text-align: center;
    color: var(--muted);
    animation: pythomic-fade-up 0.6s var(--ease-out) both;
}
.py-empty svg {
    color: var(--border);
    animation: pythomic-float 3s var(--ease) infinite;
}
.py-empty p:first-of-type {
    background: var(--brand-grad);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ============================================================
   10. FAB — botão flutuante de criar post (pulso + gradiente)
   ============================================================ */
.py-fab {
    position: fixed;
    right: 18px;
    /* Sem barra inferior: o FAB fica direto no canto inferior direito. */
    bottom: calc(18px + var(--safe-bottom));
    z-index: 45;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    color: #ffffff;
    background: var(--brand-grad);
    background-size: 200% 200%;
    box-shadow: var(--shadow-brand);
    display: flex;
    align-items: center;
    justify-content: center;
    animation: pythomic-fab-in 0.5s var(--ease-spring) 0.2s both,
               pythomic-btn-grad 5s var(--ease) infinite,
               pythomic-fab-pulse 2.4s var(--ease) infinite;
    transition: transform 0.2s var(--ease-bounce);
}
.py-fab:hover { transform: scale(1.1) rotate(90deg); }
.py-fab:active { transform: scale(0.9); }
@keyframes pythomic-fab-in {
    from { opacity: 0; transform: scale(0) rotate(-180deg); }
    to   { opacity: 1; transform: scale(1) rotate(0); }
}
@keyframes pythomic-fab-pulse {
    0%, 100% { box-shadow: var(--shadow-brand), 0 0 0 0 rgba(91, 91, 246, 0.45); }
    50%      { box-shadow: var(--shadow-brand), 0 0 0 14px rgba(91, 91, 246, 0); }
}

/* ============================================================
   11. MODAIS — top sheets (slide down do topo + bounce + blur)
   ============================================================ */
.py-overlay {
    position: fixed;
    inset: 0;
    background: rgba(8, 9, 18, 0.55);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    z-index: 100;
    padding: 0;
    animation: pythomic-overlay-in 0.28s var(--ease) both;
}
@keyframes pythomic-overlay-in { from { opacity: 0; } to { opacity: 1; } }
.py-modal {
    background: var(--card-glass-strong);
    backdrop-filter: saturate(180%) blur(24px);
    -webkit-backdrop-filter: saturate(180%) blur(24px);
    border: 1px solid var(--border);
    border-radius: 0 0 var(--radius-xl) var(--radius-xl);
    padding: calc(22px + var(--safe-top)) 22px calc(26px + var(--safe-bottom));
    width: 100%;
    max-width: 560px;
    max-height: 92vh;
    overflow-y: auto;
    position: relative;
    box-shadow: var(--shadow-lg);
    animation: pythomic-sheet-down 0.38s var(--ease-spring) both;
}
/* Puxador (drag handle) no topo do top sheet */
.py-modal::before {
    content: "";
    display: block;
    width: 42px;
    height: 5px;
    border-radius: 5px;
    background: var(--border);
    margin: 0 auto 18px;
    transition: background 0.2s var(--ease);
}
.py-modal:hover::before { background: var(--muted); }
@keyframes pythomic-sheet-down {
    from { transform: translateY(-100%); opacity: 0.3; }
    to   { transform: translateY(0); opacity: 1; }
}
.py-modal-close { position: absolute; top: calc(16px + var(--safe-top)); right: 14px; z-index: 2; }
.py-modal-title {
    margin: 2px 0 4px;
    text-align: center;
    font-size: 18px;
    font-weight: 700;
    animation: pythomic-fade-up 0.4s var(--ease-out) 0.1s both;
}
.py-modal-sub {
    margin: 0 0 16px;
    text-align: center;
    color: var(--muted);
    font-size: 13px;
    animation: pythomic-fade-up 0.4s var(--ease-out) 0.15s both;
}
.py-divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
.py-section-title { margin: 18px 0 11px; font-size: 14px; font-weight: 700; }
.py-counter { font-size: 12px; color: var(--muted); text-align: right; margin: -4px 0 8px; }
.py-counter-full { color: var(--danger); font-weight: 700; }
.py-attached {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--success);
    margin: 0 0 8px;
    animation: pythomic-pop-in 0.3s var(--ease-bounce);
}
.py-attached svg { color: var(--success); }
.py-thumb {
    width: 76px;
    height: 76px;
    object-fit: cover;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    display: block;
    margin-bottom: 8px;
    animation: pythomic-pop-in 0.3s var(--ease-bounce);
}
.py-stats {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin: 0 0 16px;
    flex-wrap: wrap;
    animation: pythomic-fade-up 0.4s var(--ease-out) 0.1s both;
}
.py-stat {
    background: var(--input-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 11px 17px;
    font-size: 13px;
    color: var(--muted);
    text-align: center;
    min-width: 72px;
    transition: transform 0.2s var(--ease-bounce), border-color 0.2s var(--ease), box-shadow 0.2s var(--ease);
    animation: pythomic-pop-in 0.4s var(--ease-bounce) both;
}
.py-stat:hover { transform: translateY(-2px); border-color: var(--brand); box-shadow: var(--shadow-sm); }
.py-stat:active { transform: scale(0.94); }
.py-stat:nth-child(1) { animation-delay: 0.12s; }
.py-stat:nth-child(2) { animation-delay: 0.18s; }
.py-stat:nth-child(3) { animation-delay: 0.24s; }
.py-stat:nth-child(4) { animation-delay: 0.30s; }
.py-stat strong {
    color: var(--text);
    font-size: 17px;
    display: block;
    line-height: 1.1;
    margin-bottom: 2px;
}

/* ============================================================
   12. PERFIL — linha do perfil, avatar, nome, meta
   ============================================================ */
.py-avatar-wrap { display: flex; justify-content: center; margin: 0 0 8px; }
.py-profile-row { display: flex; align-items: center; gap: 14px; margin: 6px 0 12px; }
.py-profile-row .py-avatar { width: 78px; height: 78px; }
.py-profile-info { min-width: 0; flex: 1; }
.py-profile-name {
    font-weight: 700;
    font-size: 17px;
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.py-profile-meta { font-size: 12px; color: var(--muted); }

/* ============================================================
   13. SKELETON SHIMMER + SPINNER (estados de carregamento)
   ============================================================ */
.py-skeleton {
    background: linear-gradient(90deg, var(--input-bg) 25%, var(--border) 37%, var(--input-bg) 63%);
    background-size: 400% 100%;
    animation: pythomic-shimmer 1.4s ease infinite;
    border-radius: var(--radius-sm);
}
@keyframes pythomic-shimmer {
    0%   { background-position: 100% 50%; }
    100% { background-position: 0 50%; }
}

/* ============================================================
   14. ADAPTATIVO — tablet/paisagem mantém mobile-only
   ============================================================ */
@media (min-width: 600px) {
    .py-main { max-width: 640px; }
    .py-card { margin: 22px 16px 0; }
    .py-modal { max-width: 620px; }
    .py-auth { max-width: 480px; }
    .py-fab { right: 24px; width: 60px; height: 60px; }
}
/* Feed SEMPRE em coluna única (mobile-only): o grid de 2 colunas em paisagem
   foi removido a pedido — não há mais "posts duplos" em telas maiores. */
@media (min-width: 1024px) {
    .py-main { max-width: 760px; }
    .py-auth { max-width: 500px; }
}

/* Telefone (≤480px): interface um pouco maior e mais confortável de tocar/ler.
   Tablets NÃO são afetados — o usuário reportou que ficaram bons como estão. */
@media (max-width: 480px) {
    .py-header { padding: 14px 14px; padding-top: calc(14px + var(--safe-top)); }
    .py-header .py-icon-btn { padding: 11px; }   /* ~40px -> ~44px (alvo de toque) */
    .py-avatar { width: 50px; height: 50px; }
    .py-user-name { font-size: 15px; }
    .py-user-meta { font-size: 13px; }
    .py-caption { font-size: 15px; }
    .py-likes { font-size: 15px; }
    .py-tab svg { width: 24px; height: 24px; }
    .py-tab { font-size: 12px; }
}

/* ============================================================
   15. ACESSIBILIDADE — respeita prefers-reduced-motion
   ============================================================ */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001ms !important;
        scroll-behavior: auto !important;
    }
    body::before, body::after { animation: none !important; }
}
"""
