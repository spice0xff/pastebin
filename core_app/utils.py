import datetime
from datetime import timezone

from .models import Paste


# Список последних 10 публичных доступных по времени паст.
def base_context(request):
    paste_list = Paste.objects.filter(
        access_only_from_link=False,
        access_time__gte=datetime.datetime.now(timezone.utc),
    ).order_by('-id')[:10]

    return {
        'paste_list': paste_list
    }
