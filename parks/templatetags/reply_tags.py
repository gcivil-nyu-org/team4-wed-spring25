from django import template

register = template.Library()


@register.inclusion_tag("parks/reply_thread.html", takes_context=True)
def render_replies(context, reply):
    return {
        "reply": reply,
        "user": context.get("user"),
        "park": context.get("park"),
        "request": context.get("request"),  # Optional: if your template needs it
    }
