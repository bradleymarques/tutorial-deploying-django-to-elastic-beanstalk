from typing import Any, Dict

from django.contrib.auth.models import User
from django.views.generic import TemplateView


class HelloWorldView(TemplateView):
    template_name = "hello_world/hello_world.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({"user_count": User.objects.count()})
        return context
