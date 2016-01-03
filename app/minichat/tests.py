from django.core.urlresolvers import reverse
from django.test import TestCase
from minichat.models import Message
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.utils.lorem_ipsum import words


class ViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_archives(self):
        response = self.client.get(reverse('minichat_archives'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('minichat_archives'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_latests(self):
        response = self.client.get(reverse('minichat_latests'))
        self.assertEqual(response.status_code, 200)

    def test_post_login_required(self):
        url = reverse('minichat_post')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login') + '?next=' + url, 302, 200)

    def test_post_login(self):
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': 'Hello World!'})
        self.assertRedirects(response, reverse('minichat_post'), target_status_code=200)
        self.assertEqual(Message.objects.last().text, 'Hello World!')
        self.client.logout()

    def test_userslist_invalid(self):
        response = self.client.get(reverse('minichat_userslist'))
        self.assertEqual(response.status_code, 404)

    def test_userslist_smallquery(self):
        response = self.client.get(reverse('minichat_userslist'), {'query': 'a'})
        self.assertEqual(response.status_code, 404)

    def test_userslist(self):
        response = self.client.get(reverse('minichat_userslist'), {'query': 'abc'})
        self.assertEqual(response.status_code, 200)


class AnchorTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.users = User.objects.all()

    def test_single(self):
        anchored = self.users[1]
        formats = [
            'Hello @{}!',
            'Hello@{}!',
            '@{}',
            '@@{}',
            '@{}@',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(anchored.get_username()))
            self.assertListEqual(message.parse_anchors(), [anchored], msg='format: %s' % frmt)

    def test_multiple(self):
        formats = [
            'Hello @{0} @{1}',
            '@{0}@{1}',
            '@{0}@{0}@{1}',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(self.users[0].get_username(), self.users[1].get_username()))
            self.assertListEqual(message.parse_anchors(), [self.users[0], self.users[1]], msg='format: %s' % frmt)

    def test_invalid(self):
        anchored = self.users[:2]
        formats = [
            '@{0}abcdefghijklmnopqrstuvwxyz', # ... and expect this is not a valid username
            '@ {0}',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(anchored[0].get_username(), anchored[1].get_username()))
            self.assertListEqual(message.parse_anchors(), [], msg='format: %s' % frmt)


class SubstituteTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.users = User.objects.all()
        self.author = self.users[0]
        Message(user=self.author, text='Older message').save()
        Message(user=self.author, text='Hello World!').save()

    def test_no_message(self):
        message = Message(user=self.users[1], text='s/nothing/todo')
        self.assertIsNone(message.substitute())

    def test_message_selection(self):
        # Create new message from another author
        other_message = Message(user=self.users[1], text='Another message')
        other_message.save()

        message = Message(user=self.author, text='s/nothing/todo')
        modified = message.substitute()

        self.assertEqual(modified.user, self.author)
        self.assertEqual(modified.text, 'Hello World!')

        # Remove the other message
        other_message.delete()

    def test_valid_substitution(self):
        message = Message(user=self.author, text='s/World!/Universe!?')
        self.assertEqual(message.substitute().text, 'Hello Universe!?')

    def test_valid_multiple_substitutions(self):
        message = Message(user=self.author, text='s/o/p')
        self.assertEqual(message.substitute().text, 'Hellp Wprld!')

    def test_empty_pattern(self):
        message = Message(user=self.author, text='s/o/')
        self.assertEqual(message.substitute().text, 'Hell Wrld!')

    def test_empty_match(self):
        message = Message(user=self.author, text='s//o')
        self.assertIsNone(message.substitute())

    def test_no_match(self):
        message = Message(user=self.author, text='s/bye/nothing')
        self.assertEqual(message.substitute().text, 'Hello World!')


class ApiTests(APITestCase):
    fixtures = ['devel']

    def setUp(self):
        self.users = User.objects.all()
        self.author = self.users[0]

    def test_latest_minichat(self):
        Message.objects.all().delete()
        for i in range(0,57):
            Message(user=self.author, text=words(5, False)).save()
        Message(user=self.author, text='Last message').save()

        response = self.client.get('/minichat/api/latest/', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 58)
        self.assertEqual(len(response.data['results']), 10)

        first_message = response.data['results'][0]
        # Striclty check the fields to avoir extra disclosure (field id is not sent)
        self.assertEqual(list(first_message.keys()), ['user', 'text', 'date'])

        # Striclty check the fields to avoir extra disclosure (we should only send username
        # and profile, not password, email, ...)
        self.assertEqual(list(first_message['user'].keys()), ['username', 'profile'])


        # Striclty check the fields to avoir extra disclosure (we should only send avatar,
        # not last_visit, ...)
        self.assertEqual(list(first_message['user']['profile'].keys()), ['avatar'])

        self.assertEqual(first_message['text'], 'Last message')


