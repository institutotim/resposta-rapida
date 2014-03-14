# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Field.desc'
        db.add_column('forms_field', 'desc',
                      self.gf('django.db.models.fields.CharField')(max_length=30, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Field.desc'
        db.delete_column('forms_field', 'desc')


    models = {
        'forms.condition': {
            'Meta': {'ordering': "['order']", 'object_name': 'Condition'},
            'action': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'extra_vars': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logic': ('django.db.models.fields.SmallIntegerField', [], {}),
            'new_value': ('django.db.models.fields.CharField', [], {'max_length': '160', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'param': ('picklefield.fields.PickledObjectField', [], {})
        },
        'forms.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('picklefield.fields.PickledObjectField', [], {}),
            'value_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'})
        },
        'forms.field': {
            'Meta': {'object_name': 'Field'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '160', 'blank': 'True'}),
            'conditions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['forms.Condition']", 'symmetrical': 'False'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'field_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['forms.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '30'})
        },
        'forms.form': {
            'Meta': {'object_name': 'Form'},
            'ans_default': ('django.db.models.fields.CharField', [], {'default': "'Muito obrigado, recebemos sua mensagem com sucesso.'", 'max_length': '160', 'blank': 'True'}),
            'ans_incorrect_num_fields': ('django.db.models.fields.CharField', [], {'default': "'Voce enviou um numero incorreto de campos. Por favor, verifique sua tabela.'", 'max_length': '160', 'blank': 'True'}),
            'ans_negative_confirmation': ('django.db.models.fields.CharField', [], {'default': "'Obrigado, recebemos seu pedido de cancelamento com sucesso.'", 'max_length': '160', 'blank': 'True'}),
            'ans_positive_confirmation': ('django.db.models.fields.CharField', [], {'default': "'Obrigado, recebemos sua confirma\\xc3\\xa7\\xc3\\xa3o com sucesso.'", 'max_length': '160', 'blank': 'True'}),
            'ans_unknown_confirmation': ('django.db.models.fields.CharField', [], {'default': "'Desculpe, n\\xc3\\xa3o conseguimos entender o c\\xc3\\xb3digo de confirma\\xc3\\xa7\\xc3\\xa3o enviado, por favor use %s para confirmar, %s para cancelar.'", 'max_length': '160', 'blank': 'True'}),
            'ans_waiting_confirmation': ('django.db.models.fields.CharField', [], {'default': "'Esses dados est\\xc3\\xa3o corretos?'", 'max_length': '160', 'blank': 'True'}),
            'conditions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['forms.Condition']", 'symmetrical': 'False'}),
            'confirmation_conditions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'form_confirmations'", 'symmetrical': 'False', 'to': "orm['forms.Condition']"}),
            'enable_java': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enable_sms': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enable_wap': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enable_web': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'negative_confirmation_list': ('picklefield.fields.PickledObjectField', [], {}),
            'positive_confirmation_list': ('picklefield.fields.PickledObjectField', [], {}),
            'requires_confirmation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'separator': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '1'})
        },
        'forms.submission': {
            'Meta': {'object_name': 'Submission'},
            'context': ('picklefield.fields.PickledObjectField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'data': ('picklefield.fields.PickledObjectField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forms.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'remote_last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'remote_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        'forms.tasksran': {
            'Meta': {'object_name': 'TasksRan'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forms.Submission']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks_ran'", 'to': "orm['forms.TimedTask']"})
        },
        'forms.timedtask': {
            'Meta': {'object_name': 'TimedTask'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['forms.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'once': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'run_after_min': ('django.db.models.fields.IntegerField', [], {}),
            'status_to_change': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'submission_status': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['forms']