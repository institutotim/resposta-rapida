from rapidsms.backends.http.forms import BaseHttpForm
from django import forms


class PurebrosForm(BaseHttpForm):
    pb_id = forms.CharField()
    mo_datetime = forms.DateTimeField()
    mo_body = forms.CharField()
    mo_source = forms.CharField()
    mo_carrier = forms.CharField()

    def get_incoming_data(self):
        fields = self.cleaned_data.copy()
        identity = fields['mo_carrier'] + "." + fields['mo_source']
        connections = self.lookup_connections([identity])

        return {'connection': connections[0],
                'text': fields['mo_body'],
                'fields': fields}