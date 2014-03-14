#!/usr/bin/env python
# encoding: utf-8
# vim: ai ts=4 sts=4 et sw=4


from django import forms


# the built-in FileField doesn't specify the 'size' attribute, so the
# widget is rendered at its default width -- which is too wide for our
# form. this is a little hack to shrink the field.
class SmallFileField(forms.FileField):
    def widget_attrs(self, widget):
        return { "size": 10 }


class MessageForm(forms.Form):
    identity = forms.CharField(
        label="Telefone",
        max_length=100,
        help_text="O telefone que o sistema irá " +
                  "pensar que esta mensagem veio.")

    text = forms.CharField(
        label="Mensagem",
        required=False,
        widget=forms.widgets.Textarea({
            "cols": 30,
            "rows": 4 }))