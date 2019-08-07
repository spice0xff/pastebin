from django.forms import ModelForm

from core_app.models import Paste


# Форма добавлния пасты.
class PasteForm(ModelForm):
    class Meta:
        model = Paste
        fields = ['text', 'access_period', 'access_only_from_link']
