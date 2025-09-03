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
        
from django import forms
from .models import Type

class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = ["name_type"]  # <-- phải trùng với field trong model



from django import forms
from .models import Reflect, ReflectResponse

# Form tạo phản ánh (dành cho sinh viên)
class ReflectForm(forms.ModelForm):
    class Meta:
        model = Reflect
        fields = ["title", "content", "type", "bo_mon", "attachment"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4}),
        }


# Form phản hồi phản ánh (dành cho giáo viên)
class ReflectResponseForm(forms.ModelForm):
    class Meta:
        model = ReflectResponse
        fields = ["content", "attachment"]  # Không đưa rating vào form này

class ResponseRatingForm(forms.ModelForm):
    class Meta:
        model = ReflectResponse
        fields = ["rating"]

from django import forms
from .models import Survey

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'link', 'status', 'end_date']
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
