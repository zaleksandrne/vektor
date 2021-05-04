from django.db import models
from django.contrib.postgres.fields import ArrayField, array
from itertools import zip_longest
from django.db.models.signals import m2m_changed, post_save

# Create your models here.

class Vector(models.Model):
    
    array = ArrayField(models.IntegerField())

    def __str__(self):
        return str(self.array)


class Operation(models.Model):
    CHOICES = (('add', 'addition'), ('mult', 'multiplication'))
    type = models.CharField(max_length=100, choices=CHOICES)
    vectors = models.ManyToManyField(
        Vector,
        verbose_name='vectors'
        )
    array = ArrayField(models.IntegerField(), blank=True, null=True)
    new_vector = models.OneToOneField(Vector,
                                      on_delete = models.CASCADE,
                                      related_name='vector',
                                      blank=True,
                                      null=True
                                      )


    def __str__(self):
        return str(self.array)


def vectors_changed(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and pk_set:
        print(pk_set)
        for item in pk_set:
            vector = Vector.objects.get(id=item)
            if instance.type == 'add':
                c = [x+y for x, y in zip_longest(instance.array, vector.array, fillvalue=0)]
            elif instance.type == 'mult':
                c = [x * y for x, y in zip_longest(instance.array, vector.array, fillvalue=1)]
            instance.array = c
        vector = Vector.objects.create(array=instance.array)
        instance.new_vector = vector
        instance.save()


m2m_changed.connect(vectors_changed, sender=Operation.vectors.through)


def save_operation(sender, instance, **kwargs):
    o = Operation.objects.filter(vectors__id=instance.id)
    if o:
        for operation in o:
            operation.array = []
            operation.new_vector.array = []
            for vector in operation.vectors.all():
                if operation.type == 'add':
                    c = [x+y for x, y in zip_longest(operation.array, vector.array, fillvalue=0)]
                elif operation.type == 'mult':
                    c = [x * y for x, y in zip_longest(operation.array, vector.array, fillvalue=1)]
                operation.array = c
            operation.save()
            operation.new_vector.array = c
            operation.new_vector.save()
            #print(operation.vectors.all())
            #o.update(array = )
    #print(a)


post_save.connect(save_operation, sender=Vector)