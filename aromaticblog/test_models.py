from django.test import TestCase
import unittest
from django.contrib.auth.models import User
from .models import Post


class TestModels(TestCase):
    """ Testing of a Post model """

    @classmethod
    def setUpTestData(cls):
        """ Set up to be used throughout the whole TestCase """
        cls.author1 = User.objects.create(is_superuser=post.author)
        cls.author = Post.objects.create(author=cls.author1)
        cls.post = Post.objects.create(
            title='A test', author=cls.author, content='This is a test.')
  
        def test_if_post_has_required_author(self):
            """ Post must have an author - admin """
            self.assertEqual(self.post.author.name, self.author_)

if __name__ == '__main__':
    unittest.main()
