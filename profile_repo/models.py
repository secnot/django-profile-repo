# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from model_utils.models import TimeStampedModel

__all__ = ['get_profile', 'set_profile', 'del_profile', 'get_or_create_profile',
        'get_all_profiles']

def extract_content_type(model):
    return ContentType.objects.get_for_model(model)

class UserProfileManager(models.Manager):
    def get_profile(self, user, model_class=None):
        """
        Arguments:
            user (User instance):
            model_class (model class): Class for the data to retrieve
        
        Returns:
            instance of model_class stored for User

        Exceptions:
            ObjectDoesNotExist: No model of the given class
        """
        profile = self.get(user = user,
                content_type=extract_content_type(model_class))
        return profile.content_object
   
    def get_all_profiles(self, user):
        profiles = self.filter(user=user)
        return [p.content_object for p in profiles]

    def set_profile(self, user, model):
        """
        Arguments:
            user (User instance):
            model (Model instance):
        """
        try:
            user_profile = self.get(user=user,
                    content_type=extract_content_type(model))
            user_profile.content_object = model
            user_profile.save()
        except ObjectDoesNotExist:
            user_profile = self.create(user=user, content_object=model)

    def del_profile(self, user, model_class, delete_model=False):
        """
        Delete reference to model from profile, referenced model is left 
        in db unless, unless 'delete_model=True'

        Arguments:
            user (User object)
            model_class(Model Class)
            delete_model(Boolean)

        """
        profile = self.get(user = user,
                content_type=extract_content_type(model_class))
        referenced = profile.content_object
        profile.delete()

        if delete_model:
            referenced.delete()

    def get_or_create_profile(self, user, model_class, defaults=None):
        """
        Arguments:
            user (User instance):
            model_class (Model class):
            defaults (None | dict): Defaults used to initialize the model
                fields when a new one must be created.
        """

        if not defaults:
            defaults={}

        try:
            profile = self.get_profile(user, model_class)
        except ObjectDoesNotExist:
            profile = model_class.objects.create(**defaults)
            try:
                self.set_profile(user, profile)
            except Exception as err:
                profile.delete()
                raise err

        return profile

class UserProfile(TimeStampedModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = UserProfileManager()
    class Meta:
        unique_together = ("user", "content_type")
        #index_together = ["user", "content_type"]

    def __str__(self):
        classname = self.content_type.model_class().__name__
        return "{} -> {}".format(self.user.username, classname)



def get_profile(user, model_class):
    return UserProfile.objects.get_profile(user, model_class)

def get_all_profiles(user):
    return UserProfile.objects.get_all_profiles(user)

def set_profile(user, model):
    return UserProfile.objects.set_profile(user, model)

def del_profile(user, model_class, delete_model=False):
    UserProfile.objects.del_profile(user, model_class, delete_model)

def get_or_create_profile(user, model_class, defaults=None):
    return UserProfile.objects.get_or_create_profile(user, model_class, defaults)
