import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import robo.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robocontest_clone.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            robo.routing.websocket_urlpatterns
        )
    )
})
