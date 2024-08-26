from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User 
from .models import BlogPost, Comment
# za testiranje korisnika
from django.test import Client
from django.urls import reverse
from django.contrib import messages
from django.core import mail
from .forms import RegisterUserForm
from django.contrib.auth import logout

#from django.middleware.csrf import get_token
from django.http import HttpResponseRedirect


class BlogPostTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='pera', password='kojot2323', is_staff=True)
        self.client.force_authenticate(user=self.user)

        self.non_staff_user = User.objects.create_user(username='marko', password='sifra2323', is_staff=False)

        self.blog_post = BlogPost.objects.create(title='Test naslov', content='Test content', author=self.user)

    # PRIKAZIVANJE SVI POSTOVA
    def test_get_blogposts(self):
        url = '/api/blogposts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # jedan post
        self.assertEqual(response.data[0]['title'], 'Test naslov')

    # NEMA POSTOVA ZA PRIKAZIVANJE
    def test_get_no_blogposts(self):
        BlogPost.objects.all().delete()
        url = '/api/blogposts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # nema postova

    # KREIRANJE POSTA
    def test_blogpost_create(self):
        # uspesno
        url = '/api/blogposts/'
        data = {'title': 'Test Post', 'content': 'Test content'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 2)
        self.assertEqual(BlogPost.objects.last().title, 'Test Post')

        # bez naslova
        url = '/api/blogposts/' 
        data = {'title': '', 'content': 'Test content.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # izlogovan
        self.client.logout()
        url = '/api/blogposts/' 
        data = {'title': 'Test Post', 'content': 'Test content'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # nije staff
        self.client.force_authenticate(user=self.non_staff_user)
        url = '/api/blogposts/'
        data = {'title': 'Test post non staff', 'content': 'Test content.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # DETALJI ODREDJENOG POSTA
    def test_blogpost_details(self):
        # nepostojeci post
        nepostojeci_post = 23
        url = f'/api/blogposts/{nepostojeci_post}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # prikaz postojeceg posta
        url2 = f'/api/blogposts/{self.blog_post.id}/'
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    # AZURIRANJE POSTA
    def test_blogpost_update(self):
        # invalid data
        url = f'/api/blogposts/{self.blog_post.id}/'
        response = self.client.get(url)
        data = {'title': '', 'content': 'Updated content'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # staff
        response = self.client.get(url)
        data = {'title': 'Updated title', 'content': 'Updated content'}
        response = self.client.put(url, data, format='json')
        self.blog_post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.blog_post.title, 'Updated title')
        self.assertEqual(self.blog_post.content, 'Updated content')

        # unauthenticated
        self.client.logout()
        response = self.client.get(url)
        data = {'title': 'Updated title unauthenticated', 'content': 'Updated content unauthenticated'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # non staff 
        self.client.force_authenticate(user=self.non_staff_user)
        url = f'/api/blogposts/{self.blog_post.id}/'
        data = {'title': 'Updated title non staff', 'content': 'Updated content'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    # BRISANJE POSTA
    # staff
    def test_blogpost_delete_staff(self):
        url = f'/api/blogposts/{self.blog_post.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BlogPost.objects.count(), 0)
        self.assertFalse(BlogPost.objects.filter(id=self.blog_post.id).exists())

    # unauthenticated
    def test_blogpost_delete_unauthenticated(self):
        self.client.logout()
        url = f'/api/blogposts/{self.blog_post.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(BlogPost.objects.filter(id=self.blog_post.id).exists())
    
    # non staff
    def test_blogpost_delete_non_staff(self):
        self.client.logout()
        self.client.force_authenticate(user=self.non_staff_user)
        url = f'/api/blogposts/{self.blog_post.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(BlogPost.objects.filter(id=self.blog_post.id).exists())

    # DODAVANJE KOMENTARA
    # authenticated
    def test_add_comment_authenticated(self):
        self.client.logout()
        self.client.force_authenticate(user=self.non_staff_user)

        url = f'/api/blogposts/{self.blog_post.id}/comments/'

        data = {'content': 'Test comment auth.'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Test comment auth.')
        self.assertEqual(comment.blog_post, self.blog_post) # ovde proveravam 'Test naslov'
    
    # staff
    def test_add_comment_staff(self):

        url = f'/api/blogposts/{self.blog_post.id}/comments/'

        data = {'content': 'Test comment staff.'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Test comment staff.')
        self.assertEqual(comment.blog_post, self.blog_post)
    
    # unauthenticated
    def test_add_comment_authenticated(self):
        self.client.logout()
        url = f'/api/blogposts/{self.blog_post.id}/comments/'
        data = {'content': 'Test comment unauth.'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Comment.objects.count(), 0)

    # invalid data
    def test_add_comment_invalid_data(self):

        url = f'/api/blogposts/{self.blog_post.id}/comments/'

        data = {'content': ''}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Comment.objects.count(), 0)


    # AZURIRANJE KOMENTARA
    def test_update_comment_staff(self):     
        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.user,  
            content='Original Comment'
        )

        url = f'/api/comments/{self.comment.id}/'

        data = {'content': 'Updated comment staff'}

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # proveravam da li je komentar ažuriran
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment staff')


    def test_update_comment_invalid_data(self):        
        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.user,  
            content='Original Comment'
        )

        url = f'/api/comments/{self.comment.id}/'

        data = {'content': ''}

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Original Comment')
    
    def test_update_comment_non_staff(self):

        self.client.logout()
        self.client.force_authenticate(user=self.non_staff_user)

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.non_staff_user,  
            content='Original Non Staff Comment'
        )

        url = f'/api/comments/{self.comment.id}/'

        data = {'content': 'Updated comment non staff'}

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # proveravam da li je komentar azuriran
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment non staff')

    
    def test_update_staff_comment_non_staff(self):
        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.user,
            content='Test comment staff'
        )

        self.client.logout()
        self.client.force_authenticate(user=self.non_staff_user)

        url = f'/api/comments/{self.comment.id}/'

        data = {'content': 'Updated comment non staff'}

        response = self.client.put(url, data, format='json')

        # nece proci
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # komentar ne treba da bude azuriran
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Test comment staff')


    def test_update_user_comment_staff(self):
        
        self.client.logout()
        self.client.force_authenticate(user=self.non_staff_user)

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.non_staff_user,
            content='Test comment non staff'
        )

        self.client.logout()
        self.client.force_authenticate(user=self.user)

        url = f'/api/comments/{self.comment.id}/'
        data = {'content': 'Updated comment staff'}

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Test comment non staff')
    
    def test_update_comment_unauthenticated(self):

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.user,
            content='Test comment staff'
        )

        self.client.logout()

        url = f'/api/comments/{self.comment.id}/'
        data = {'content': 'Updated comment unauth'}

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Test comment staff')

    # KOMENTAR (NE) POSTOJI

    def test_get_comment_not_exists(self):

        url = f'/api/comments/999/'
        data = {'content': 'Updated comment staff'}
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    

    def test_get_comment_exists(self):

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.user,
            content='Test comment staff'
        )

        url = f'/api/comments/{self.comment.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    #BRISANJE KOMENTARA

    # unauthenticated
    def test_delete_comment_unauthenticated(self):

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.user, 
            content='Original Comment'
        )

        self.client.logout()

        url = f'/api/comments/{self.comment.id}/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Komentar treba da postoji
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())


    def test_staff_delete_user_comment(self):

        self.client.force_authenticate(user=self.non_staff_user)

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.non_staff_user,
            content='Original Comment'
        )

        self.client.logout()
        self.client.force_authenticate(user=self.user)

        url = f'/api/comments/{self.comment.id}/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Komentar treba da postoji
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
    
    def test_user_delete_staff_comment(self):

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.user,
            content='Test comment'
        )

        self.client.logout()
        self.client.force_authenticate(user=self.non_staff_user)

        url = f'/api/comments/{self.comment.id}/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Komentar treba da postoji
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_user(self):
        self.client.logout()
        self.client.force_authenticate(user=self.non_staff_user)

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.non_staff_user,
            content='Test comment'
        )
        
        url = f'/api/comments/{self.comment.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    
    def test_delete_comment_staff(self):

        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            author=self.user,
            content='Test comment'
        )
        
        url = f'/api/comments/{self.comment.id}/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())


# TESTIRANJE KORISNIKA
class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register_user')  # moja putanja iz

    def test_registration_successful(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'old': 25,
            'email': 'testuser@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123'
        }
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 302)  # Kad se preusmera status je 302


    def test_registration_successful_message(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'old': 25,
            'email': 'testuser@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123'
        }
        response = self.client.post(self.register_url, form_data, follow=True)
        # Check if success message is in response
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Uspesna registracija! Mozete se prijaviti.')

    def test_registration_error_message(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'old': 150,
            'email': 'invalid-email',
            'password1': 'password123',
            'password2': 'differentpassword'
        }
        response = self.client.post(self.register_url, form_data)
        # Check if error message is in response
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Greska u formi. Pokusajte ponovo')



    def test_registration_invalid_form(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'old': 150,  # Invalid 'old' value, should be less than 100
            'email': 'invalid-email',
            'password1': 'password123',
            'password2': 'differentpassword'  # Passwords do not match
        }
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 200)  # Should render the same page with errors (status code 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

        form = response.context.get('form')
        if form:
            print(form.errors)
        
        # Check for form errors
        self.assertIn('old', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)


# LOGIN TEST

class LoginUserTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_valid_user(self):
        response = self.client.post(reverse('login_user'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)  # redirect kod 302
        self.assertRedirects(response, reverse('blogposts'))
        self.assertIn('_auth_user_id', self.client.session)  # proveravam da li je ulogovan

    def test_login_invalid_user(self):
        response = self.client.post(reverse('login_user'), {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login_user'))
        self.assertIn('Greska pri logovanju. Pokusaj ponovo.', [msg.message for msg in messages.get_messages(response.wsgi_request)])
        #ovo linijom dolazim do poruku koja se ispisuje ako podaci nisu dobri.

    def test_login_missing_username(self):
        response = self.client.post(reverse('login_user'), {
            'username': '',
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, reverse('login_user'))
        self.assertIn('Unesi korisnicko ime i lozinku', [msg.message for msg in messages.get_messages(response.wsgi_request)])

    def test_login_missing_password(self):
        """Test login with missing password"""
        response = self.client.post(reverse('login_user'), {
            'username': self.username,
            'password': ''
        })
        self.assertEqual(response.status_code, 302)  # redirekt 302
        self.assertRedirects(response, reverse('login_user'))
        self.assertIn('Unesi korisnicko ime i lozinku', [msg.message for msg in messages.get_messages(response.wsgi_request)])

    def test_login_get_method(self):
        response = self.client.get(reverse('login_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

# LOGOUT TEST

class LogoutUserTestCase(TestCase):
    def setUp(self):
        # Korisnik
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def test_logout_post(self):
        # POST
        response = self.client.post(reverse('logout_user'))
        self.assertEqual(response.status_code, 302)  # preusmeravanje
        self.assertRedirects(response, reverse('login_user'))
        self.assertNotIn('_auth_user_id', self.client.session)  # Da li je korisnik odjavljen

    def test_logout_get(self):
        #GET
        response = self.client.get(reverse('logout_user'))
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'login.html')  # da li je dobio trazenu stranicu

    

