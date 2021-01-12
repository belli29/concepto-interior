from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('sold', 'reserved')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
        self.fields['image_one'].label = "Image" \
            " (please use pictures 500px*500px for better results)"
        self.fields['l'].label = "Long in cms"
        self.fields['h'].label = "High in cms"
        self.fields['w'].label = "Wide in cms"