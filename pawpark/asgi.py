import os
import django
django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import parks.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawpark.settings")



application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(parks.routing.websocket_urlpatterns)
        ),
    }
)
