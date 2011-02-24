# -*- coding: utf-8 -*-
"""
    Tests for tipfy.ext.auth
"""
import os
import sys
import unittest

from nose.tools import raises

from gaetestbed import DataStoreTestCase

from tipfy.ext.auth import login_required, user_required, admin_required
from tipfy import RequestHandler
from tipfy.ext.auth import AppEngineAuthMixin


class TestAuthDecorators(DataStoreTestCase, unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_login_required_success_gae(self):
        class MyHandler(RequestHandler, AppEngineAuthMixin):
            @login_required
            def get(self, **kwargs):
                return Response('success')

    def test_login_required_failure_gae(self):
        pass

    def test_user_required_success_gae(self):
        pass

    def test_user_required_failure_gae(self):
        pass

    def test_admin_required_success_gae(self):
        pass

    def test_admin_required_failure_gae(self):
        pass

    def test_login_required_success_multi(self):
        pass

    def test_login_required_failure_multi(self):
        pass

    def test_user_required_success_multi(self):
        pass

    def test_user_required_failure_multi(self):
        pass

    def test_admin_required_success_multi(self):
        pass

    def test_admin_required_failure_multi(self):
        pass
