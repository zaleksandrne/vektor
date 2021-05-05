from django.db import models
from django.contrib.postgres.fields import ArrayField
from itertools import zip_longest
from django.db.models.signals import m2m_changed, post_save, pre_delete


class Vector(models.Model):
    array = ArrayField(models.IntegerField())

    def __str__(self):
        return f'id:{self.id}, arr:{self.array}'


class Operation(models.Model):
    CHOICES = (('add', 'addition'), ('mult', 'multiplication'))
    type = models.CharField(max_length=100, choices=CHOICES)
    vectors = models.ManyToManyField(
        Vector,
        verbose_name='Vector'
        )
    array = ArrayField(models.IntegerField(), blank=True, null=True)
    new_vector = models.OneToOneField(Vector,
                                      on_delete=models.CASCADE,
                                      related_name='vector',
                                      blank=True,
                                      null=True
                                      )

    def delete(self, *args, **kwargs):
        self.new_vector.delete()

    def __str__(self):
        return f'id:{self.id}, type:{self.type}, new_vector:{self.array}'


def vectors_changed(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and pk_set:
        print(pk_set)
        for item in pk_set:
            vector = Vector.objects.get(id=item)
            if instance.type == 'add':
                arr = [x+y for x, y in zip_longest(
                    instance.array, vector.array, fillvalue=0)]
            elif instance.type == 'mult':
                arr = [x * y for x, y in zip_longest(
                    instance.array, vector.array, fillvalue=1)]
            instance.array = arr
        vector = Vector.objects.create(array=instance.array)
        instance.new_vector = vector
        instance.save()
        for item in pk_set:
            vector = Vector.objects.get(id=item)
            print(len(instance.array))
            print(len(vector.array))
            vector.array += (len(instance.array) - len(vector.array)) * [0]
            vector.save()


def save_operation(sender, instance, **kwargs):
    o = Operation.objects.filter(vectors__id=instance.id)
    for operation in o:
        operation.array = []
        operation.new_vector.array = []
        for vector in operation.vectors.all():
            if operation.type == 'add':
                arr = [x+y for x, y in zip_longest(
                    operation.array, vector.array, fillvalue=0)]
            elif operation.type == 'mult':
                arr = [x * y for x, y in zip_longest(
                    operation.array, vector.array, fillvalue=1)]
            operation.array = arr
        operation.save()
        operation.new_vector.array = arr
        operation.new_vector.save()
        for vector in operation.vectors.all():
            print(vector)
            vector.array += (len(operation.array) - len(vector.array)) * [0]
            post_save.disconnect(save_operation, sender=Vector)
            vector.save()
            post_save.connect(save_operation, sender=Vector)


def vector_delete_pre(sender, instance, **kwargs):
    o = Operation.objects.filter(vectors__id=instance.id)
    for operation in o:
        if operation.vectors.all().count() < 3:
            operation.delete()
        else:
            operation.array = []
            operation.new_vector.array = []
            for vector in operation.vectors.exclude(id=instance.id):
                if operation.type == 'add':
                    c = [x+y for x, y in zip_longest(
                        operation.array, vector.array, fillvalue=0)]
                elif operation.type == 'mult':
                    c = [x * y for x, y in zip_longest(
                        operation.array, vector.array, fillvalue=1)]
                operation.array = c
            operation.save()
            operation.new_vector.array = c
            operation.new_vector.save()


m2m_changed.connect(vectors_changed, sender=Operation.vectors.through)
post_save.connect(save_operation, sender=Vector)
pre_delete.connect(vector_delete_pre, sender=Vector)
