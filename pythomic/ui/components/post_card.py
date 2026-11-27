"""Card de post do feed."""

from reactpy import component, html, use_state

from ...database import delete_post, toggle_follow, toggle_like
from ...uploads import delete_media
from ..icons import HeartIcon, IconEye


@component
def PostCard(post, current_user, refresh, feed_version, on_open_profile):
    """Card de post do feed.

    Os estados de curtida guardam o id do post e a versão do feed: como os
    componentes são reconciliados por posição na lista, isso impede que a
    curtida de um post apareça em outro ao inserir/atualizar o feed — e
    ressincroniza os contadores quando o usuário clica em "Atualizar Feed".
    """
    like_state, set_like_state = use_state(None)
    if (
        like_state is None
        or like_state["post_id"] != post["id"]
        or like_state["feed_version"] != feed_version
    ):
        like_state = {
            "post_id": post["id"],
            "feed_version": feed_version,
            "liked": bool(post["is_liked"]),
            "count": post["likes_count"],
        }
    pop_key, set_pop_key = use_state(0)

    # Confirmação de exclusão em 2 cliques. O estado carrega o post_id para que
    # o "Confirmar?" não vaze para outro post quando a lista é reconciliada por
    # posição após uma exclusão (mesma defesa do like_state contra o bug de
    # reconciliação do ReactPy).
    del_state, set_del_state = use_state(None)
    if del_state is None or del_state["post_id"] != post["id"]:
        del_state = {"post_id": post["id"], "confirming": False}

    def handle_like(e):
        liked = toggle_like(current_user["id"], post["id"])
        set_like_state(
            {
                "post_id": post["id"],
                "feed_version": like_state["feed_version"],
                "liked": liked,
                "count": like_state["count"] + (1 if liked else -1),
            }
        )
        set_pop_key(lambda k: k + 1)  # remonta o coração e reanima o "pop"

    def handle_follow(e):
        toggle_follow(current_user["id"], post["user_id"])
        refresh()

    def handle_delete(e):
        # 1.º clique: arma a confirmação (botão vira "Confirmar?").
        # 2.º clique: exclui o post do banco + apaga a mídia do disco.
        if not del_state["confirming"]:
            set_del_state({"post_id": post["id"], "confirming": True})
            return
        media = delete_post(current_user["id"], post["id"])
        if media:
            delete_media(media)
        refresh()

    is_own_post = post["user_id"] == current_user["id"]

    media_element = None
    if post["media"]:
        if post["media"].lower().endswith((".mp4", ".webm")):
            media_element = html.video(
                {"src": post["media"], "controls": True, "preload": "metadata", "class": "py-media"}
            )
        else:
            media_element = html.img(
                {"src": post["media"], "alt": "Mídia do post", "class": "py-media"}
            )

    # Slot do cabeçalho do card: post de outro usuário → Seguir/Seguindo;
    # post próprio → Excluir (2 cliques). Antes este slot ficava vazio nos
    # posts do próprio perfil.
    if is_own_post:
        action_btn = html.button(
            {
                "class": "py-btn-delete"
                + ("" if not del_state["confirming"] else " py-btn-delete-confirm"),
                "on_click": handle_delete,
                "title": "Excluir este post"
                if not del_state["confirming"]
                else "Clique novamente para confirmar a exclusão",
                "aria-label": "Excluir post",
            },
            "Confirmar?" if del_state["confirming"] else "Excluir",
        )
    else:
        action_btn = html.button(
            {
                "class": "py-btn-follow py-btn-following" if post["is_following"] else "py-btn-follow",
                "on_click": handle_follow,
            },
            "Seguindo" if post["is_following"] else "Seguir",
        )

    user_meta = f"{post['followers_count']} seguidores"
    if post["time_label"]:
        user_meta += f" · {post['time_label']}"

    legenda = None
    if post["text"]:
        legenda = html.p(
            {"class": "py-caption"},
            html.strong({}, post["name"]),
            " " + post["text"],
        )

    return html.div(
        {"class": "py-card"},
        html.div(
            {"class": "py-post-header"},
            html.div(
                {
                    "class": "py-post-user",
                    "on_click": lambda e: on_open_profile(post["user_id"]),
                    "title": "Ver perfil",
                },
                html.div(
                    {"class": "py-avatar"},
                    html.img({"src": post["profile_pic"], "alt": post["name"]}),
                ),
                html.div(
                    {"style": {"minWidth": "0"}},
                    html.div({"class": "py-user-name"}, post["name"]),
                    html.div({"class": "py-user-meta"}, user_meta),
                ),
            ),
            action_btn,
        ),
        media_element,
        html.div(
            {"class": "py-post-actions"},
            html.button(
                {"class": "py-like-btn", "on_click": handle_like, "title": "Curtir"},
                html.span({"class": "py-pop", "key": f"heart-{pop_key}"}, html.span({}, HeartIcon(like_state["liked"]))),
            ),
            html.span({"class": "py-likes"}, str(like_state["count"])),
            html.span(
                {"class": "py-views", "title": "Visualizações"},
                IconEye(16),
                str(post["views_count"]),
            ),
        ),
        legenda,
    )
