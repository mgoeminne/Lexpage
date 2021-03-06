from django import forms
from .widgets import DateTimePicker
from .search import SEARCH
import datetime


class SearchForm(forms.Form):
    query_text = forms.CharField(required=True, label='Texte à rechercher', help_text='Les termes doivent être séparés par un espace, et peuvent être groupés à l\'aide de guillemets.')
    target = forms.ChoiceField(label='Rechercher dans...', choices=[(i, v['title']) for i, v in enumerate(SEARCH)])
    author = forms.CharField(required=False, label='Filtrer par auteur', help_text='Laissez vide si vous ne souhaitez pas ce critère.')
    date_start = forms.DateField(required=False, label='Filtrer par date, début de la période', help_text='Laissez vide si vous ne souhaitez pas ce critère.',
                                 widget=DateTimePicker(options={'format': 'DD/MM/YYYY', 'pickTime': False}))
    date_end = forms.DateField(required=False, label='Filtrer par date, fin de la période', help_text='Laissez vide si vous ne souhaitez pas ce critère.',
                               widget=DateTimePicker(options={'format': 'DD/MM/YYYY', 'pickTime': False}))

    def clean_query_text(self):
        if len(self.cleaned_data['query_text'].strip()) == 0:
            raise forms.ValidationError('Ce champ ne peut pas être vide.')
        else:
            return self.cleaned_data['query_text']

    def clean_date_start(self):
        if not self.cleaned_data['date_start']:
            return datetime.date.min
        return self.cleaned_data['date_start']

    def clean_date_end(self):
        if not self.cleaned_data['date_end']:
            return datetime.date.today() + datetime.timedelta(1)
        return self.cleaned_data['date_end']

    def clean_target(self):
        return int(self.cleaned_data['target'])

