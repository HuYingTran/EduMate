from django import forms
from .models import Reflect, Document

class ReflectForm(forms.ModelForm):
    class Meta:
        model = Reflect
        fields = ['title', 'content']  # các trường mà sinh viên nhập khi gửi phản ánh
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Nội dung phản ánh'}),
        }


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'type', 'file']