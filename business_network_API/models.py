# Business network API

# Django
from django.db import models
from django.db.models import Manager, Q, QuerySet
from django.utils import timezone


class VisibilityQuerySet(QuerySet):
    """
    Queryset to manage the visibility that the entities 
    childs of VisibilityModel has in the platform.
    """

    def delete(self):
        return super(VisibilityQuerySet, self).update(
            state = VisibilityModel.States.DELETED
        )

    def hard_delete(self):
        return super(VisibilityQuerySet, self).delete()

    def alive(self):
        return self.exclude( 
            state = VisibilityModel.States.DELETED
        )

    def dead(self):
        return self.filter( 
            state = VisibilityModel.States.DELETED 
        )


class VisibilityManager(Manager):
    """
    Father manager of all the models that can be deleted or hide.
    Helps to manage the visibility that the entities 
    childs of VisibilityModel has in the platform.
    """

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(VisibilityManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return VisibilityQuerySet(self.model).exclude( 
                state = VisibilityModel.States.DELETED 
            )

        return VisibilityQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class VisibilityModel(models.Model):
    """
    Father model of all the models that can be deleted or hide.
    Helps to manage the visibility that the
    entities has in the platform. Useful for
    accesibility and recover of information.
    """

    class States(models.TextChoices):
        """
        Enum for the types of states that 
        could have a model in the platform.
        """

        PRIVATE = 'PRIV', 'Private'
        OPEN = 'OPEN', 'Open'
        DELETED = 'DEL', 'Deleted'
        
    state = models.CharField(
        max_length = 4,
        choices = States.choices,
        default = States.OPEN
    )

    changed_at = models.DateTimeField(auto_now = True)

    objects = VisibilityManager()
    all_objects = VisibilityManager(alive_only = False)

    class Meta:
        abstract = True

    def delete(self):
        self.state = self.States.DELETED
        self.save()

    def hard_delete(self):
        super(VisibilityModel, self).delete()