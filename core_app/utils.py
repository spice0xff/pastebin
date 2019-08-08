import datetime
from datetime import timezone

from .models import Paste
from .forms import FindForm


# Базовый контекст рендеринга.
def base_context(request):
    # Список последних 10 публичных доступных по времени паст.
    paste_list = Paste.objects.filter(
        access_only_from_link=False,
        private=False,
        access_time__gte=datetime.datetime.now(timezone.utc),
    ).order_by('-id')[:10]

    # Список последних 10 паст аутентифицированного владельца.
    owner_paste_list = {}
    if request.user.is_authenticated:
        owner_paste_list = Paste.objects.filter(
            owner=request.user
        ).order_by('-id')[:10]

    # Форма поиска.
    find_form = FindForm()

    return {
        'paste_list': paste_list,
        'owner_paste_list': owner_paste_list,
        'find_form': find_form
    }
