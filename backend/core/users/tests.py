from django.contrib.auth import get_user_model
from django.test import TestCase


class UserTests(TestCase):

    def test_create_user(self):

        user = get_user_model().objects.create_user(
            username='test_user_1',
            email='test_user_1@email.com',
            first_name='test_first_name',
            last_name='test_last_name',
            password='test_password',
        )

        self.assertEqual(user.username, 'test_user_1')
        self.assertEqual(user.email, 'test_user_1@email.com')
        self.assertEqual(user.first_name, 'test_first_name')
        self.assertEqual(user.last_name, 'test_last_name')
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):

        admin_user = get_user_model().objects.create_superuser(
            username='superadmin',
            email='super_admin@mail.com',
            first_name='admin_first_name',
            last_name='admin_last_name',
            password='test_password',
        )

        self.assertEqual(admin_user.username, 'superadmin')
        self.assertEqual(admin_user.email, 'super_admin@mail.com')
        self.assertEqual(admin_user.first_name, 'admin_first_name')
        self.assertEqual(admin_user.last_name, 'admin_last_name')
        self.assertTrue(admin_user.is_superuser)
