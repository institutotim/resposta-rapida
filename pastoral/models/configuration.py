# encoding: utf-8

from django.db import models, DatabaseError
from picklefield import PickledObjectField
from annoying.functions import get_object_or_None
from django.db.models.signals import post_save
from django.conf import settings

local_cache = {}
for d in settings.DEFAULT_CONFIGURATION.values():
    local_cache.update(d)


class Configuration(models.Model):
    VALUE_TYPES = (
        (1, 'Boolean'),
        (2, 'Text'),
        (3, 'Number'),
    )

    key = models.CharField(max_length=25, unique=True)
    value = PickledObjectField()
    value_type = models.SmallIntegerField(choices=VALUE_TYPES, default=2)
    label = models.CharField(max_length=50)

    def set(self, key, val):
        self.set_item(key, val)

    def get(self, key):
        if not key in local_cache:
            return None

        return local_cache[key]["val"]

    @staticmethod
    def get_item(key):
        if not key in local_cache:
            return None

        return local_cache[key]

    @staticmethod
    def set_item(key, val, val_type=None, label=None):
        item = get_object_or_None(Configuration, key=key)
        if item:
            item.value = val
            item.value_type = item.value_type or val_type
            item.label = label or item.label
            item.save()
        else:
            if not val_type:
                if isinstance(val, basestring):
                    val_type = 2
                elif isinstance(val, bool):
                    val_type = 1
                elif isinstance(val, int):
                    val_type = 3

            Configuration.objects.create(key=key, value=val, value_type=val_type, label=(label or key))

    class Meta:
        app_label = "forms"


def update_cache(sender=None, **kwargs):
    try:
        items = Configuration.objects.all()
        for item in items:
            local_cache[item.key] = {"val": item.value, "type": item.value_type}
    except DatabaseError:
        pass


Config = Configuration()

# Insert default settings into database in case it isnt there yet
try:
    if Configuration.objects.count() < len(local_cache):
        for k, v in local_cache.iteritems():
            Config.set_item(k, v["val"], v["type"], v["label"])
except DatabaseError:
    pass

post_save.connect(update_cache, sender=Configuration)
update_cache()