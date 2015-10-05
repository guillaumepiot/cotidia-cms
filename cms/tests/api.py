# -*- coding: utf-8 -*-
import os, json, io

from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase, Client
from PIL import Image as PILImage

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from account.models import User
from cms.models import Page, PageTranslation, Image

# Create your tests here.
class PageTranslationTests(APITestCase):

    fixtures = [
        'account/fixtures/auth.json',
        'account/fixtures/account.json',
        ]

    def setUp(self):
        # Add a default user and generate an authentication token
        self.user = User.objects.get(email="page@editor.com")
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()

        c = Client()
        c.login(username="page@editor.com", password="demo")

        #
        # Create a default page
        #
        data = {
            'display_title': "Home",
            'home': 1,
            'template': "cms/page.html"
        }

        url = reverse('cms-admin:page_add')
        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)

        page = Page.objects.filter().first()

        #
        # Set a translation title
        #
        data = {
            'title': "Home",
        }

        url = reverse(
            'cms-admin:page_title_add', 
            kwargs={'page_id': page.id, 'lang':"en"})

        response = c.post(url, data)
        self.assertEqual(response.status_code, 302)


    def test_add(self):

        """ Test if we can add, retrieve and list """

        #
        # Authenticate the client
        #
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        translation = PageTranslation.objects.filter().first()
        
        # Create the add URL
        url = reverse('cms-api:update', kwargs={'id':translation.id})

        regions = json.dumps([
            {
                "article": """<h1>5 rules for naming variables</h1>
                    <p class=\"article__by-line\">
                        by <b>Anthony Blackshaw</b> 18th January 2015
                    </p>"""
            }
        ])

        data = {
            'regions': regions,
        }
        

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ImageUploadTests(APITestCase):

    fixtures = [
        'account/fixtures/auth.json',
        'account/fixtures/account.json',
        ]

    def setUp(self):
         # Add a default user and generate an authentication token
        self.user = User.objects.get(email="page@editor.com")
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        
    def test_upload_image(self):

        #
        # Authenticate the client
        #
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        #
        # Upload Image
        #

        url = reverse('cms-api:image-add')

        file_obj = io.BytesIO()
        image = PILImage.new("RGBA", size=(100,50), color=(256,0,0))
        image.save(file_obj, 'png')

        file_obj.seek(0)
        
        django_friendly_file = ContentFile(file_obj.read(), 'test.png')

        data = {
            'width': 100,
            'image': django_friendly_file
            }

        # Upload a file with an authenticated user
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['size'], [100, 50])
        self.assertEqual(response.data['display_width'], 100)

        image_id = response.data['id']


        #
        # Crop Image
        #

        url = reverse('cms-api:image-update', args=[image_id])

        data = {
            'width': 10,
            'crop': '0,0,0.1,0.1'
            }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['size'], [10, 5])
        self.assertEqual(response.data['display_width'], 10)

        #
        # Rotate Image
        #

        url = reverse('cms-api:image-update', args=[image_id])

        data = {
            'width': 5,
            'direction': 'CW'
            }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['size'], [5, 10])
        self.assertEqual(response.data['display_width'], 5)

        # assert unauthenticated user can not upload file
        self.client.logout()
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
