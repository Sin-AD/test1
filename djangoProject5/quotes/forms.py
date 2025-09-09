from django import forms
from .models import Quote, Source
from django.core.exceptions import ValidationError

class QuoteForm(forms.ModelForm):
    new_source_name = forms.CharField(
        required=False,
        label="Новый источник (если не выбран существующий)",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    new_source_type = forms.ChoiceField(
        required=False,
        choices=Source.TYPE_CHOICES,
        label="Тип нового источника",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    source = forms.ModelChoiceField(
        queryset=Source.objects.all(),
        required=False,
        label="Выбрать существующий источник",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Quote
        fields = ["text", "source", "weight", "new_source_name", "new_source_type"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "weight": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }

    def clean(self):
        cleaned = super().clean()
        source = cleaned.get("source")
        new_source_name = cleaned.get("new_source_name", "").strip()

        if not source and not new_source_name:
            raise ValidationError("Укажите существующий источник или введите новый.")

        if source and Quote.objects.filter(source=source).count() >= 3:
            raise ValidationError("У этого источника уже есть 3 цитаты — нельзя добавить больше.")

        if new_source_name:
            existing = Source.objects.filter(name__iexact=new_source_name).first()
            if existing:
                if Quote.objects.filter(source=existing).count() >= 3:
                    raise ValidationError("У этого источника уже есть 3 цитаты — нельзя добавить больше.")
                cleaned["source"] = existing
            else:
                source_type = cleaned.get("new_source_type") or "other"
                new_source = Source.objects.create(name=new_source_name, type=source_type)
                cleaned["source"] = new_source

        return cleaned

    def save(self, commit=True):
        self.instance.source = self.cleaned_data["source"]
        return super().save(commit=commit)
