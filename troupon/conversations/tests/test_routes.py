from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from conversations.models import Message


class MessageRouteTestCase(TestCase):
    """Tests merchant/message/<m_id> endpoint
    Ensures that merchant can view thread and reply to thread
    """
    @classmethod
    def setUpClass(cls):
        """Setup the test driver with reusable objects once for use in
        every test case.
        """
        cls.msg_stub = {
            'subject': 'Test subject',
            'body': 'Test body',
            'type': 1,
        }  # message stub
        cls.subject_slug = slugify(cls.msg_stub['subject'])
        cls.admin = User.objects.create_user(
            username='testadmin', email='testadmin@test.com',
            password='password1')
        cls.merchant = User.objects.create_user(
            username='testmerchant', email='testmerchant@test.com',
            password='password2')
        cls.client = Client()
        super(MessageRouteTestCase, cls).setUpClass()

    def test_merchant_can_reply_to_message_sent_by_admin(self):
        """Tests that a message can be replied to and as such spawning a conversation
        """

        # login administrator
        response = self.client.post(
            reverse('login'),
            {'username': self.admin.username, 'password': 'password1'})
        self.assertRedirects(response, reverse('homepage'), status_code=302)

        # post message to merchant
        self.msg_stub['recipient'] = self.merchant.username
        response = self.client.post(
            reverse('messages'),
            self.msg_stub)

        latest_msg = Message.objects.latest('sent_at')
        self.assertRedirects(
            response,
            reverse(
                'message', kwargs={'m_id': latest_msg.id}
            ),
            status_code=302
        )

        # logout administrator
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'), status_code=302)

        # login merchant
        response = self.client.post(
            reverse('login'),
            {'username': self.merchant.username, 'password': 'password2'})
        self.assertRedirects(response, reverse('homepage'), status_code=302)

        # reply message from administrator
        self.msg_stub['parent_msg'] = Message.objects.latest('sent_at').id
        self.msg_stub['recipient'] = self.admin.username
        response = self.client.post(
            reverse('message', kwargs={'m_id': self.msg_stub['parent_msg']}),
            self.msg_stub, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.msg_stub['body'])

        # logout merchant
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'), status_code=302)

    @classmethod
    def tearDownClass(cls):
        super(MessageRouteTestCase, cls).tearDownClass()


class MessagesRouteTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup the test driver with reusable objects once for use in
        every test case.
        """
        cls.msg_stub = {
            'subject': 'Test subject',
            'body': 'Test body',
        }  # message stub
        cls.subject_slug = slugify(cls.msg_stub['subject'])
        cls.admin = User.objects.get(username='testadmin')
        cls.merchant = User.objects.get(username='testmerchant')
        cls.client = Client()
        super(MessagesRouteTestCase, cls).setUpClass()

    def test_admin_can_post_message_to_merchant(self):
        """Tests admin can post message to merchant
        """
        # login administrator
        response = self.client.post(
            reverse('login'),
            {'username': self.admin.username, 'password': 'password1'})
        self.assertEqual(response.status_code, 302)

        self.msg_stub['recipient'] = self.merchant.username
        response = self.client.post(
            reverse('messages'),
            self.msg_stub)

        lastest_msg = Message.objects.latest('sent_at')
        self.assertRedirects(
            response,
            reverse(
                'message',
                kwargs={'m_id': lastest_msg.id}
            ),
            status_code=302,
        )

        # logout administrator
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'), status_code=302)

    def test_admin_can_read_message_from_merchant(self):
        """Tests admin can read message from merchant
        """
        # login merchant
        response = self.client.post(
            reverse('login'),
            {'username': self.merchant.username, 'password': 'password2'})
        self.assertRedirects(response, reverse('homepage'), status_code=302)
        # post message to admin
        self.msg_stub['recipient'] = self.admin.username
        response = self.client.post(
            reverse('messages'),
            self.msg_stub)

        lastest_msg = Message.objects.latest('sent_at')
        self.assertRedirects(
            response,
            reverse(
                'message',
                kwargs={'m_id': lastest_msg.id}
            ),
            status_code=302
        )

        # logout merchant
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'), status_code=302)

        # login administrator
        response = self.client.post(
            reverse('login'),
            {'username': self.admin.username, 'password': 'password1'})
        self.assertEqual(response.status_code, 302)

        # read messages
        response = self.client.get(
            reverse(
                'message', kwargs={'m_id': lastest_msg.id}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.msg_stub['body'])

        # logout administrator
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'), status_code=302)

    def test_merchant_can_post_message_to_admin(self):
        """Tests merchant can post message to admin
        """

        # login merchant
        response = self.client.post(
            reverse('login'),
            {'username': self.merchant.username, 'password': 'password2'})
        self.assertEqual(response.status_code, 302)

        self.msg_stub['recipient'] = self.admin.username
        response = self.client.post(
            reverse('messages'),
            self.msg_stub, follow=True)

        lastest_msg = Message.objects.latest('sent_at')
        self.assertRedirects(
            response,
            reverse(
                'message',
                kwargs={'m_id': lastest_msg.id}
            ),
            status_code=302,
        )

        # logout merchant
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'), status_code=302)

    def test_merchant_can_read_message_from_admin(self):
        """Tests merchant can read message from admin
        """
        # login administrator
        response = self.client.post(
            reverse('login'),
            {'username': self.admin.username, 'password': 'password1'})
        self.assertRedirects(response, reverse('homepage'), status_code=302)

        # post message to merchant
        self.msg_stub['recipient'] = self.merchant.username
        response = self.client.post(
            reverse('messages'),
            self.msg_stub)

        latest_msg = Message.objects.latest('sent_at')
        self.assertRedirects(
            response,
            reverse(
                'message',
                kwargs={'m_id': latest_msg.id}
            ),
            status_code=302
        )

        # logout admin
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'), status_code=302)

        # login merchant
        response = self.client.post(
            reverse('login'),
            {'username': self.merchant.username, 'password': 'password2'})
        self.assertEqual(response.status_code, 302)

        # read messages
        response = self.client.get(
            reverse(
                'message', kwargs={'m_id': latest_msg.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.msg_stub['body'])

        # logout merchant
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'), status_code=302)

    @classmethod
    def tearDownClass(cls):
        super(MessagesRouteTestCase, cls).tearDownClass()
