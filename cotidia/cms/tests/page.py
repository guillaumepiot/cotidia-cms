from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from cms.models import Page, PageTranslation
from account.models import User

class PageTests(TestCase):


    def setUp(self):

        # Create a default user
        self.user = User.objects.create(
            username="page@editor.com",
            email="page@editor.com",
            is_staff=True,
            is_active=True,
            is_superuser=True)

        self.user.set_password('demo')
        self.user.save()

    def test_add_page(self):
        """
        Test if we can add a page in the admin
        """
        c = Client()

        url = reverse('cms-admin:page-add')

        c.login(username="page@editor.com", password='demo')

        response = c.get(url)
        # Test that the page load first
        self.assertEqual(response.status_code, 200)

        data = {
            'display_title': "Home",
            'home': 1,
            'template': "cms/page.html"
        }

        # Test that we can save this data
        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        # Test that a new page now exists
        pages = Page.objects.filter()
        self.assertEqual(pages.count(), 1)

        page = pages.first()

        # Test the values have been saved correctly against the booking
        self.assertEqual(page.display_title, "Home")
        self.assertEqual(page.home, True)
        self.assertEqual(page.template, "cms/page.html")

        #
        # Try to add another page which is set as home too
        # The page should not redirect
        #

        data = {
            'display_title': "About",
            'home': 1,
            'template': "cms/page.html"
        }

        # Test that we can save this data
        response = c.post(url, data)
        self.assertEqual(response.status_code, 200)

        # Test that there's still only one appointment
        pages = Page.objects.filter()
        self.assertEqual(pages.count(), 1)


    def test_add_translation(self):
        """
        Test if we can add a translation in the admin
        """
        c = Client()
        c.login(username="page@editor.com", password='demo')

        url = reverse('cms-admin:page-add')

        data = {
            'display_title': "Home",
            'home': 1,
            'template': "cms/page.html"
        }

        # Test that we can save this data
        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        page = Page.objects.filter().first()

        url = reverse('cms-admin:page-update', kwargs={'pk':page.id})

        # Test that we can update the page details

        data = {
            'display_title': "Home (updated)",
            'home': 1,
            'template': "cms/page.html"
        }

        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        page = Page.objects.filter().first()
        self.assertEqual(page.display_title, "Home (updated)")

        # Test that we can add a url
        url = reverse(
            'cms-admin:page-url-add',
            kwargs={'page_id':page.id, 'lang':"en"}
            )

        data = {
            'slug': "home",
        }

        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        translation = PageTranslation.objects.filter().first()

        self.assertEqual(translation.slug, "home")

        # Test that we can update a url
        url = reverse(
            'cms-admin:page-url-update',
            kwargs={'page_id':page.id, 'lang':"en", 'trans_id':translation.id}
            )

        data = {
            'slug': "home-updated",
        }

        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        translation = PageTranslation.objects.filter().first()
        self.assertEqual(translation.slug, "home-updated")


    def test_publish_page(self):
        """
        Test if we can add a translation in the admin
        """
        c = Client()
        c.login(username="page@editor.com", password='demo')

        url = reverse('cms-admin:page-add')

        data = {
            'display_title': "Home",
            'home': 1,
            'template': "cms/page.html"
        }

        # Test that we can save this data
        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        page = Page.objects.filter().first()

        # Test that we can add a url
        url = reverse(
            'cms-admin:page-url-add',
            kwargs={'page_id':page.id, 'lang':"en"}
            )

        data = {
            'slug': "home",
        }

        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        translation = PageTranslation.objects.filter().first()

        self.assertEqual(translation.slug, "home")

        # Test that we can publish the page
        url = reverse(
            'cms-admin:page-publish',
            kwargs={'page_id':page.id}
            )

        data = {}

        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        pages = Page.objects.filter()
        self.assertEqual(pages.count(), 2)

        # Test that we can unpublish the page
        url = reverse(
            'cms-admin:page-unpublish',
            kwargs={'page_id':page.id}
            )

        data = {}

        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        pages = Page.objects.filter()
        self.assertEqual(pages.count(), 2)
        self.assertFalse(pages[0].published)


