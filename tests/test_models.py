#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-profile-repo
------------

Tests for `django-profile-repo` models module.
"""
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.test import TestCase


from profile_repo.models import *
from profile_repo.models import UserProfile


class TestDjango_profile(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test_user")

        # Use two built in models as profile
        self.profile_a1 = Permission.objects.first()
        self.profile_a2 = Permission.objects.last()

        # A Different content type
        self.profile_b1 = User.objects.first()

    def test_set_profile(self):

        # A new UserProfile is created when none existed
        set_profile(self.user, self.profile_a1)
        profile = get_profile(self.user, Permission)
        
        self.assertEqual(self.profile_a1, profile)

        # The profile value is substituted when one
        # already existed.
        set_profile(self.user, self.profile_a2)
        profile = get_profile(self.user, Permission)

        self.assertEqual(self.profile_a2, profile)

        self.assertEqual(UserProfile.objects.all().count(), 1)

        # Try with a second content type
        set_profile(self.user, self.profile_b1)

        profile = get_profile(self.user, User)
        self.assertEqual(self.profile_b1, profile)
        self.assertEqual(UserProfile.objects.all().count(), 2)

    def test_get_profile(self):
        set_profile(self.user, self.profile_a1)
        
        # Retrieve value using model class
        profile = get_profile(self.user, Permission)
        self.assertEqual(self.profile_a1, profile)

        # Retrive using model instance
        profile = get_profile(self.user, self.profile_a2)
        self.assertEqual(self.profile_a1, profile)

        # Raise exception when does not exist
        with self.assertRaises(ObjectDoesNotExist):
            profile = get_profile(self.user, User)

    def test_get_all_profiles(self):
        profiles = get_all_profiles(self.user)
        self.assertEqual(len(profiles), 0)

        # With one profile stored
        set_profile(self.user, self.profile_a1)
        profiles = get_all_profiles(self.user)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0], self.profile_a1)

        set_profile(self.user, self.profile_a2)
        profiles = get_all_profiles(self.user)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0], self.profile_a2)

        # Two profile stored
        set_profile(self.user, self.profile_b1)
        profiles = get_all_profiles(self.user)
        self.assertEqual(len(profiles), 2)
        self.assertTrue(self.profile_a2 in profiles)
        self.assertTrue(self.profile_b1 in profiles)

        # Delete one of the profiles
        del_profile(self.user, self.profile_a2.__class__)
        profiles = get_all_profiles(self.user)
        self.assertEqual(len(profiles), 1)
        self.assertTrue(self.profile_b1 in profiles)

    def test_del_profile(self):
        # Test referenced model is not delete, only the reference
        set_profile(self.user, self.profile_a1)
        set_profile(self.user, self.profile_b1)
        

        self.assertTrue(User.objects.filter(id=self.profile_b1.id).exists())
        self.assertEqual(len(get_all_profiles(self.user)), 2)
        del_profile(self.user, User)
        self.assertTrue(User.objects.filter(id=self.profile_b1.id).exists()) 
        self.assertEqual(len(get_all_profiles(self.user)), 1)

        # Also delete referenced model   
        self.assertTrue(Permission.objects.filter(id=self.profile_a1.id).exists())
        del_profile(self.user, Permission, delete_model=True)
        self.assertFalse(Permission.objects.filter(id=self.profile_a1.id).exists())
        self.assertEqual(len(get_all_profiles(self.user)), 0)

    def test_get_or_create_profile(self):
        
        # Profile not availabe, a new one is created.
        get_or_create_profile(self.user, User, defaults={"username":"Rambo"})
        self.assertEqual(get_profile(self.user, User).username, "Rambo")

        # Profile already stored, check it is returned and not modified.
        profile = get_or_create_profile(self.user, User, defaults={"username":"Not Rambo"})
        self.assertEqual(profile.username, "Rambo")

    def tearDown(self):
        pass
