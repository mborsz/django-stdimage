import os
from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.contrib.auth.models import User

from .models import *
from .forms import *


IMG_DIR = os.path.join(settings.MEDIA_ROOT, 'img')


class TestStdImage(TestCase):
    def setUp(self):
        user = User.objects.create_superuser('admin', 'admin@email.com',
                                             'admin')
        user.save()
        self.client.login(username='admin', password='admin')

        self.fixtures = {}
        fixtures_dir = os.path.join(settings.MEDIA_ROOT, 'fixtures')
        fixture_paths = os.listdir(fixtures_dir)
        for fixture_filename in fixture_paths:
            fixture_path = os.path.join(fixtures_dir, fixture_filename)
            if os.path.isfile(fixture_path):
                self.fixtures[fixture_filename] = File(open(fixture_path, 'rb'))

    def tearDown(self):
        """Close all open fixtures and delete everything from media"""
        for fixture in self.fixtures.values():
            fixture.close()

        for root, dirs, files in os.walk(IMG_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))


class TestModel(TestStdImage):
    """Tests model"""

    def test_simple(self):
        """Adds image and calls save."""
        instance = SimpleModel()
        instance.image = self.fixtures['100.gif']
        instance.save()
        self.assertEqual(SimpleModel.objects.count(), 1)
        self.assertEqual(SimpleModel.objects.get(pk=1), instance)
        self.assertTrue(os.path.exists(os.path.join(IMG_DIR, 'image_1.gif')))

    def test_variations(self):
        """Adds image and checks filesystem as well as width and height."""
        instance = ResizeModel()
        instance.image = self.fixtures['600x400.jpg']
        instance.save()

        self.assertEqual(instance.image.medium.size, self.fixtures['600x400.jpg'].size)

        self.assertTrue(os.path.exists(os.path.join(IMG_DIR, 'image_1.jpeg')))
        self.assertTrue(os.path.exists(os.path.join(IMG_DIR, 'image_1.medium.jpeg')))


class TestModelForm(TestStdImage):
    """Tests ModelForm"""
    pass


class TestAdmin(TestStdImage):
    """Tests admin"""

    def test_simple(self):
        """ Upload an image using the admin interface """
        self.client.post('/admin/testproject/simplemodel/add/', {
            'image': self.fixtures['100.gif']
        })
        self.assertEqual(SimpleModel.objects.count(), 1)

    def test_empty_fail(self):
        """ Will raise an validation error and will not add an intance """
        self.client.post('/admin/testproject/simplemodel/add/', {})
        self.assertEqual(SimpleModel.objects.count(), 0)

    def test_empty_success(self):
        """ AdminDeleteModel has blan=True and will add an instance of the
        Model

        """
        self.client.post('/admin/testproject/admindeletemodel/add/', {})
        self.assertEqual(AdminDeleteModel.objects.count(), 1)

    def test_uploaded(self):
        """ Test simple upload """
        self.client.post('/admin/testproject/simplemodel/add/', {
            'image': self.fixtures['100.gif']
        })
        self.assertTrue(os.path.exists(os.path.join(IMG_DIR, 'image_1.gif')))

    def test_delete(self):
        """ Test if an image can be deleted """

        self.client.post('/admin/testproject/admindeletemodel/add/', {
            'image': self.fixtures['100.gif']
        })
        #delete
        res = self.client.post('/admin/testproject/admindeletemodel/1/', {
            'image_delete': 'checked'
        })
        self.assertFalse(os.path.exists(os.path.join(IMG_DIR,
                                                     'image_1.gif')))

    def test_thumbnail(self):
        """ Test if the thumbnail is there """

        self.client.post('/admin/testproject/thumbnailmodel/add/', {
            'image': self.fixtures['100.gif']
        })
        self.assertTrue(os.path.exists(os.path.join(IMG_DIR, 'image_1.gif')))
        self.assertTrue(os.path.exists(os.path.join(IMG_DIR, 'image_1.thumbnail.gif')))

    def test_delete_thumbnail(self):
        """ Delete an image with thumbnail """

        self.client.post('/admin/testproject/thumbnailmodel/add/', {
            'image': self.fixtures['100.gif']
        })

        #delete
        self.client.post('/admin/testproject/thumbnailmodel/1/', {
            'image_delete': 'checked'
        })
        self.assertFalse(os.path.exists(os.path.join(IMG_DIR, 'image_1.gif')))
        self.assertFalse(os.path.exists(os.path.join(IMG_DIR, 'image_1.thumbnail.gif')))