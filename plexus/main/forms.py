from django.forms import ModelForm
from .models import Alias, Contact, Server, Application


class AliasForm(ModelForm):
    class Meta:
        model = Alias
        exclude = ['ip_address', ]


class ContactForm(ModelForm):
    class Meta:
        model = Contact


class ServerForm(ModelForm):
    class Meta:
        model = Server


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
