from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    """
    Form for creating and editing Book instances.
    Used in views that require can_create and can_edit permissions.
    """

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "publication_date",
            "isbn",
            "pages",
            "cover",
            "language",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter book title"}
            ),
            "author": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter author name"}
            ),
            "publication_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "isbn": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter ISBN (optional)"}
            ),
            "pages": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Number of pages (optional)",
                }
            ),
            "cover": forms.FileInput(attrs={"class": "form-control"}),
            "language": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Language (default: English)",
                }
            ),
        }

    def clean_isbn(self):
        """
        Validate ISBN format (basic validation)
        """
        isbn = self.cleaned_data.get("isbn")
        if isbn and len(isbn) not in [10, 13]:
            raise forms.ValidationError("ISBN must be either 10 or 13 characters long.")
        return isbn


# "ExampleForm"

