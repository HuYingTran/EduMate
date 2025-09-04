from django import forms
from .models import Reflect, Document

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
        fields = ["title", "content", "type", "bo_mon", "attachment", "anonymous"]
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
