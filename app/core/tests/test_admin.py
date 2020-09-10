from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@shevo.com',
            password='test123'
        )
        # Instead of manually login the user...
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="test@shevo.com",
            password="test123",
            name="Test Shevo Name"
        )

    def test_users_lists(self):
        """Test: users are listed on user page"""
        # Generate URL for user list <- More on the django-admin doc.
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        # Below assertion also checks for HTTP 200 response.
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

# Note: We don't test out of the box functionalities.
# We rely on the django developers. We only test OUR code.

    def test_user_change_page(self):
        """Test that the user edit page workds"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        # So url = /admin/core/user/id
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test: the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
