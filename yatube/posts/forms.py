from django import forms

from .models import Comment, Group, Post


class PostForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea,
        label='Текст поста',
        help_text='Введите новый текст или отредактируйте существующий'
    )
    group = forms.ModelChoiceField(
        label='Группа, в которую входит пост',
        help_text='Выберите или измените группу, в которую входит пост',
        required=False,
        queryset=Group.objects.all()
    )
    image = forms.ImageField(
        label='Здесь загружаем картинки к постам',
        help_text='Выберите файл картинки.'
                  ' Для замены ранее загруженного файла сначала'
                  ' поставьте галочку "Очистить" и нажмите сохранить.',
        required=False
    )

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
