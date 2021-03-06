from django.db import models
from django.db.models.query import QuerySet
from django.test import TestCase

from viewflow import compat
from viewflow.models import Process


class Test(TestCase):
    def test_get_app_package_succeed(self):
        self.assertEqual(compat.get_app_package('admin'), 'django.contrib.admin')
        self.assertEqual(compat.get_app_package('auth'), 'django.contrib.auth')
        self.assertEqual(compat.get_app_package('viewflow'), 'viewflow')

    def test_get_app_package_bug112(self):
        """ Application models are located in a module that consists of multiple files """
        self.assertEqual(compat.get_app_package('tests'), 'tests')

    def test_get_app_package_missing_app_raise(self):
        self.assertRaises(Exception, compat.get_app_package, 'missing_app')

    def test_get_containing_app_data_succeed(self):
        self.assertEqual(compat.get_containing_app_data('django.contrib.admin.views'),
                         ('admin', 'django.contrib.admin'))
        self.assertEqual(compat.get_containing_app_data('django.contrib.auth.urls'),
                         ('auth', 'django.contrib.auth'))
        self.assertEqual(compat.get_containing_app_data('viewflow.flows'),
                         ('viewflow', 'viewflow'))

    def test_get_containing_app_data_bug112(self):
        """ Application models are located in a module that consists of multiple files """
        self.assertEqual(compat.get_containing_app_data('tests.models'),
                         ('tests', 'tests'))

    def test_get_containing_app_data_none_on_missing(self):
        self.assertEqual(compat.get_containing_app_data('unknown.module'),
                         (None, None))

    def test_manager_from_queryset_succeed(self):
        class TestQuerySet(QuerySet):
            def shared_method(self):
                return 'queryset'

        class TestManager(models.Manager):
            def manager_only_method(self):
                return 'manager'

        CustomManager = compat.manager_from_queryset(TestManager, TestQuerySet)
        self.assertEqual(CustomManager.__name__, 'TestManagerFromTestQuerySet')

        manager = CustomManager()
        manager.model = Process

        self.assertEqual(manager.shared_method(), 'queryset')
        self.assertEqual(manager.manager_only_method(), 'manager')
        self.assertEqual(manager.get_queryset().shared_method(), 'queryset')
        self.assertFalse(hasattr(manager.get_queryset(), 'manager_only_method'))
