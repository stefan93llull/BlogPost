from django.shortcuts import render, redirect
from .forms import RegisterUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from .models import BlogPost, Comment
from rest_framework.response import Response
from rest_framework import status
from .serializer import BlogPostSerializer, ComSerializer

# POST

# svi postovi i pravljenje novog
@api_view(['POST','GET'])
def blogposts(request):
    if request.method=='GET':
        post_list  = BlogPost.objects.all()

        if post_list.count == 0:
            return Response({'detail':'Jos nema postova.'}, status = status.HTTP_200_OK)
        
        serializer = BlogPostSerializer(post_list, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    elif request.method=='POST':
        if not request.user.is_authenticated:
            return Response({'detail':'Morate biti ulogovani!'}, status = status.HTTP_401_UNAUTHORIZED)
        
        if not request.user.is_staff:
            return Response({'detail':'Nije vam dozvoljeno pisanje postova!'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BlogPostSerializer(data = request.data, context = {'request':request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)



#pokusaj spajanja details, update, delete
@api_view(['PUT', 'GET', 'DELETE'])
def post_details(request, pk):
    if request.method=='GET':
        try:
            post = BlogPost.objects.get(id=pk)
        except BlogPost.DoesNotExist:
            return Response({'details': 'Post ne postoji!'}, status=status.HTTP_404_NOT_FOUND)

        blog_serializer = BlogPostSerializer(post)

        comms = Comment.objects.filter(blog_post_id=pk)
        comms_serializer = ComSerializer(comms, many=True)


        data = {
            'blog' : blog_serializer.data,
            'comms' : comms_serializer.data,
        }

        return Response(data, status = status.HTTP_200_OK)



    elif request.method=='PUT':
        if not request.user.is_authenticated:
            return Response({'details': 'Morate biti ulogovani!'}, status=status.HTTP_401_UNAUTHORIZED)

        if not request.user.is_staff:
            return Response({'details': 'Nije vam dozvoljeno menjanje posta!'}, status=status.HTTP_403_FORBIDDEN)

        post = BlogPost.objects.get(id=pk)
        serializer = BlogPostSerializer(instance=post, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method=='DELETE':
        post = BlogPost.objects.get(id=pk)

        if not request.user.is_authenticated:
            return Response({'detail':'Nisi ulogovan!'}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_staff:
            return Response({'detail':'Nije vam dozvoljeno brisanje postova!'}, status=status.HTTP_403_FORBIDDEN)
        
        post.delete()
        return Response({'detail':'uspesno obrisano!'}, status=status.HTTP_204_NO_CONTENT)



# KOMENTARI

@api_view(['POST', 'GET']) 
def comments(request, pk):
    if request.method == 'GET':
        try:
            post = BlogPost.objects.get(id=pk)
        except BlogPost.DoesNotExist:
            return Response({'detail': 'Post ne postoji!'}, status=status.HTTP_404_NOT_FOUND)

        blog_serializer = BlogPostSerializer(post)

        comms = Comment.objects.filter(blog_post_id=pk)
        comms_serializer = ComSerializer(comms, many=True)


        data = {
            'blog' : blog_serializer.data,
            'comms' : comms_serializer.data,
        }

        return Response(data, status = status.HTTP_200_OK)


    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail':'Nisi ulogovan!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = ComSerializer(data=request.data, context={'request': request, 'pk': pk})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET','PUT','DELETE'])
def comments_details(request, id):
    if request.method=='GET':
        try:
            com = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return Response({'detail': 'Komentar ne postoji!'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ComSerializer(com)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    if request.method=='PUT':
        com = Comment.objects.get(id=id)
        serializer = ComSerializer(com)
        if not request.user.is_authenticated:
            return Response({'detail': 'Nisi prijavljen'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user != com.author:
            return Response({'detail': 'Nije vam dozvoljeno menjanje ovog komentara', 'Komentar':serializer.data}, status=status.HTTP_403_FORBIDDEN)

        serializer = ComSerializer(instance=com, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method=='DELETE':
        if not request.user.is_authenticated:
            return Response({'detail': 'Nisi prijavljen'}, status=status.HTTP_401_UNAUTHORIZED)
        com = Comment.objects.get(id=id)
        if request.user != com.author:
            return Response({'detail': 'Nije dozvoljeno brisanje ovog komentara'}, status=status.HTTP_403_FORBIDDEN)
        
        com.delete()
        return Response({'detail': 'Uspesno obrisano'}, status=status.HTTP_204_NO_CONTENT)




#USER

def register_user(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Uspesna registracija! Mozete se prijaviti.')
            return redirect('login_user')
        else:
            messages.error(request, 'Greska u formi. Pokusajte ponovo')
    else:
        form = RegisterUserForm()

    return render(request, 'register_user.html', {'form' : form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Unesi korisnicko ime i lozinku')
            return redirect('login_user')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('blogposts')
        else:
            messages.error(request, 'Greska pri logovanju. Pokusaj ponovo.')
            return redirect('login_user')
    else:
        return render(request, 'login.html', {})



def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login_user')
    else:
        return render(request, 'login.html', {})



