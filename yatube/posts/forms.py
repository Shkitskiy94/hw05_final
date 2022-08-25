from django import forms
from django.contrib.auth import get_user_model
from posts.models import Post, Comment


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        labels = {
            'text': 'Текст поста', 'group': 'Группа',
        }

        help_texts = {
            'text': 'Текст публикации (* обязательное поле для заполнения)',
            'group': 'Группа публикации',
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if not len(text):
            raise forms.ValidationError(
                'Текст поста не может быть пустым'
            )
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Введите текст комментария',
        }
