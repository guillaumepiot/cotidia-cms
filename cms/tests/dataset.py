from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from account.models import User
from cms.models import PageDataSet

class PageDataSetTests(TestCase):

    def setUp(self):
        """
        The set up function get executed before each test. Any non-testing data
        used across all tests should be created here.
        Eg:
        self.default_data = {}
        """

        # Create a super user
        self.user = User.objects.create(
            username="admin",
            email="admin@test.com",
            is_superuser=True,
            is_active=True)
        self.user.set_password("demo")
        self.user.save()

        # Create a default object, to use with update, retrieve, list & delete
        self.object = PageDataSet.objects.create(
            name="test-dataset"
            )

        # Create the client and login the user
        self.c = Client()
        self.c.login(username=self.user.username, password='demo')

    def test_add_pagedataset(self):
        """
        Test that we can add a new object
        """

        url = reverse('cms-admin:pagedataset-add')

        # Test that the page load first
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)

        # Send data
        data = {
            'name': 'New dataset',
            'config': """[
  {
    "fieldset":"Page content",
    "fields":[
        {
            "name":"description",
            "type":"editorfield",
            "required":false
        }
    ]
  },
  {
    "fieldset":"Meta data",
    "fields":[
        {
            "name":"meta_title",
            "type":"charfield",
            "required":false
        },
        {
            "name":"meta_description",
            "type":"textfield",
            "required":false
        }
    ]
  }
]"""
        }
        response = self.c.post(url, data)
        self.assertEqual(response.status_code, 302)

        # Get the latest added object
        obj = PageDataSet.objects.filter().latest('id')
        self.assertEqual(obj.name, 'New dataset')
        self.assertEqual(obj.config, """[
  {
    "fieldset":"Page content",
    "fields":[
        {
            "name":"description",
            "type":"editorfield",
            "required":false
        }
    ]
  },
  {
    "fieldset":"Meta data",
    "fields":[
        {
            "name":"meta_title",
            "type":"charfield",
            "required":false
        },
        {
            "name":"meta_description",
            "type":"textfield",
            "required":false
        }
    ]
  }
]""")


    def test_update_pagedataset(self):
        """
        Test that we can update an existing object
        """

        url = reverse('cms-admin:pagedataset-update', 
            kwargs={
                'pk': self.object.id
                }
            )

        # Test that the page load first
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)

        # Send data
        data = {
            'name': 'other value',
            'config': self.object.config
        }
        response = self.c.post(url, data)
        print response
        self.assertEqual(response.status_code, 302)

        # Get the latest added object
        obj = PageDataSet.objects.get(id=self.object.id)
        self.assertEqual(obj.attr, 'other value')

    def test_retrieve_pagedataset(self):
        """
        Test that we can retrieve an object from its ID
        """

        url = reverse('cms-admin:pagedataset-detail', 
            kwargs={
                'pk': self.object.id
                }
            )

        # Test that the page load first
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_pagedataset(self):
        """
        Test that we can list objects
        """

        url = reverse('cms-admin:pagedataset-list')

        # Test that the page load first
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_pagedataset(self):
        """
        Test that we can delete an object
        """

        url = reverse('cms-admin:pagedataset-delete', 
            kwargs={
                'pk': self.object.id
                }
            )

        # Test that the page load first
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)

        # Action detail with POST call
        response = self.c.post(url)
        self.assertEqual(response.status_code, 302)

        # Test that the record has been deleted
        obj = PageDataSet.objects.filter(id=self.object.id)
        self.assertEqual(obj.count(), 0)