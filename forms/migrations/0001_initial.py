# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Configuration'
        db.create_table('forms_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('value', self.gf('picklefield.fields.PickledObjectField')()),
            ('value_type', self.gf('django.db.models.fields.SmallIntegerField')(default=2)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('forms', ['Configuration'])

        # Adding model 'Submission'
        db.create_table('forms_submission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forms.Form'])),
            ('data', self.gf('picklefield.fields.PickledObjectField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('context', self.gf('picklefield.fields.PickledObjectField')(blank=True)),
            ('sub_type', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('remote_last_update', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('remote_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('forms', ['Submission'])

        # Adding model 'Condition'
        db.create_table('forms_condition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('action', self.gf('django.db.models.fields.SmallIntegerField')(null=True)),
            ('param', self.gf('picklefield.fields.PickledObjectField')()),
            ('logic', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('new_value', self.gf('django.db.models.fields.CharField')(max_length=160, blank=True)),
            ('extra_vars', self.gf('picklefield.fields.PickledObjectField')(null=True)),
        ))
        db.send_create_signal('forms', ['Condition'])

        # Adding model 'Field'
        db.create_table('forms_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['forms.Form'])),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=30)),
            ('field_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=160, blank=True)),
        ))
        db.send_create_signal('forms', ['Field'])

        # Adding M2M table for field conditions on 'Field'
        db.create_table('forms_field_conditions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('field', models.ForeignKey(orm['forms.field'], null=False)),
            ('condition', models.ForeignKey(orm['forms.condition'], null=False))
        ))
        db.create_unique('forms_field_conditions', ['field_id', 'condition_id'])

        # Adding model 'Form'
        db.create_table('forms_form', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('keyword', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('separator', self.gf('django.db.models.fields.CharField')(default='.', max_length=1)),
            ('main', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requires_confirmation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('positive_confirmation_list', self.gf('picklefield.fields.PickledObjectField')()),
            ('negative_confirmation_list', self.gf('picklefield.fields.PickledObjectField')()),
            ('ans_incorrect_num_fields', self.gf('django.db.models.fields.CharField')(default='Voce enviou um numero incorreto de campos. Por favor, verifique sua tabela.', max_length=160, blank=True)),
            ('ans_positive_confirmation', self.gf('django.db.models.fields.CharField')(default='Obrigado, recebemos sua confirma\xc3\xa7\xc3\xa3o com sucesso.', max_length=160, blank=True)),
            ('ans_negative_confirmation', self.gf('django.db.models.fields.CharField')(default='Obrigado, recebemos seu pedido de cancelamento com sucesso.', max_length=160, blank=True)),
            ('ans_unknown_confirmation', self.gf('django.db.models.fields.CharField')(default='Desculpe, n\xc3\xa3o conseguimos entender o c\xc3\xb3digo de confirma\xc3\xa7\xc3\xa3o enviado, por favor use %s para confirmar, %s para cancelar.', max_length=160, blank=True)),
            ('ans_default', self.gf('django.db.models.fields.CharField')(default='Muito obrigado, recebemos sua mensagem com sucesso.', max_length=160, blank=True)),
            ('ans_waiting_confirmation', self.gf('django.db.models.fields.CharField')(default='Por favor, preencha todos os campos do formul\xc3\xa1rio.', max_length=160, blank=True)),
        ))
        db.send_create_signal('forms', ['Form'])

        # Adding M2M table for field conditions on 'Form'
        db.create_table('forms_form_conditions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm['forms.form'], null=False)),
            ('condition', models.ForeignKey(orm['forms.condition'], null=False))
        ))
        db.create_unique('forms_form_conditions', ['form_id', 'condition_id'])

        # Adding M2M table for field confirmation_conditions on 'Form'
        db.create_table('forms_form_confirmation_conditions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm['forms.form'], null=False)),
            ('condition', models.ForeignKey(orm['forms.condition'], null=False))
        ))
        db.create_unique('forms_form_confirmation_conditions', ['form_id', 'condition_id'])

        # Adding model 'TimedTask'
        db.create_table('forms_timedtask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['forms.Form'])),
            ('submission_status', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('status_to_change', self.gf('django.db.models.fields.SmallIntegerField')(null=True)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('run_after_min', self.gf('django.db.models.fields.IntegerField')()),
            ('once', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('forms', ['TimedTask'])

        # Adding model 'TasksRan'
        db.create_table('forms_tasksran', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks_ran', to=orm['forms.TimedTask'])),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forms.Submission'])),
        ))
        db.send_create_signal('forms', ['TasksRan'])


    def backwards(self, orm):
        # Deleting model 'Configuration'
        db.delete_table('forms_configuration')

        # Deleting model 'Submission'
        db.delete_table('forms_submission')

        # Deleting model 'Condition'
        db.delete_table('forms_condition')

        # Deleting model 'Field'
        db.delete_table('forms_field')

        # Removing M2M table for field conditions on 'Field'
        db.delete_table('forms_field_conditions')

        # Deleting model 'Form'
        db.delete_table('forms_form')

        # Removing M2M table for field conditions on 'Form'
        db.delete_table('forms_form_conditions')

        # Removing M2M table for field confirmation_conditions on 'Form'
        db.delete_table('forms_form_confirmation_conditions')

        # Deleting model 'TimedTask'
        db.delete_table('forms_timedtask')

        # Deleting model 'TasksRan'
        db.delete_table('forms_tasksran')


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
            'ans_waiting_confirmation': ('django.db.models.fields.CharField', [], {'default': "'Por favor, preencha todos os campos do formul\\xc3\\xa1rio.'", 'max_length': '160', 'blank': 'True'}),
            'conditions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['forms.Condition']", 'symmetrical': 'False'}),
            'confirmation_conditions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'form_confirmations'", 'symmetrical': 'False', 'to': "orm['forms.Condition']"}),
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