from rest_framework import serializers
from .models import BlogPost, Comment


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'
        read_only_fields = ('author',)
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        return BlogPost.objects.create(author=user, **validated_data)
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Naslov ne moze biti prazan!')
        return value 


class ComSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'blog_post')
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        blog_post_id = self.context.get('pk')
        blog_post = BlogPost.objects.get(id=blog_post_id)
        return Comment.objects.create(author=user, blog_post=blog_post, **validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user

        # da li je korisnik napisao taj komentar
        # if user != instance.author:
        #     raise serializers.ValidationError({'detail': 'Ne mozete updejtovati ovaj komentar.'})

        # azuriranje
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
    
    def validate_content(self, value):
        if not value.strip():  
            raise serializers.ValidationError("Ne moze biti prazan.")
        return value

    




