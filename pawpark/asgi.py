import os
import django  # noqa: E402  # Ignore the 'module level import not at top of file' error

django.setup()

from django.core.asgi import get_asgi_application  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
import parks.routing  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawpark.settings")  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(parks.routing.websocket_urlpatterns)
        ),
    }
)
