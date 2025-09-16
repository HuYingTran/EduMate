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

# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Survey, Question, Choice

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Survey Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuestionForm(forms.ModelForm):
    choices_text = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter choices (one per line)'}),
        help_text='For multiple choice questions, enter one choice per line'
    )
    
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'is_required', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        question = super().save(commit)
        
        if commit and self.cleaned_data.get('choices_text'):
            # Delete existing choices
            question.choices.all().delete()
            
            # Create new choices
            choices_lines = self.cleaned_data['choices_text'].strip().split('\n')
            for i, choice_text in enumerate(choices_lines):
                if choice_text.strip():
                    Choice.objects.create(
                        question=question,
                        text=choice_text.strip(),
                        order=i
                    )
        
        return question

QuestionFormSet = inlineformset_factory(
    Survey, 
    Question, 
    form=QuestionForm, 
    extra=1,  # Chỉ hiển thị 1 form trống ban đầu
    can_delete=True,
    max_num=20,  # Giới hạn tối đa 20 câu hỏi
    validate_max=True
)