from django import forms
from django.contrib.auth import get_user_model
from relief_app.models import Area, Category, Product, Need, AreaAdmin, Contact

User = get_user_model()


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['name', 'description', 'address', 'pincode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mumbai District'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description...'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full address...'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode/ZIP code'}),
        }


class NeedForm(forms.ModelForm):
    class Meta:
        model = Need
        fields = ['area', 'product', 'quantity', 'priority', 'status', 'notes']
        widgets = {
            'area': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional context...'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description...'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. kg, boxes, packets'}),
        }


class AreaAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password if editing'}))

    class Meta:
        model = AreaAdmin
        fields = ['name', 'email', 'area']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        admin_id = self.instance.pk
        
        # If editing, we need to allow the current user's username
        if admin_id:
            user = self.instance.user
            if User.objects.exclude(pk=user.pk).filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        area_admin = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not area_admin.pk:
            # Create a brand new CustomUser
            user = User.objects.create_user(
                username=username,
                email=area_admin.email,
                password=password or 'admin123',
                user_type='area_admin',
                first_name=area_admin.name.split()[0] if ' ' in area_admin.name else area_admin.name,
                last_name=area_admin.name.split()[-1] if ' ' in area_admin.name and len(area_admin.name.split()) > 1 else '',
                is_staff=True
            )
            area_admin.user = user
        else:
            # Update existing CustomUser
            user = area_admin.user
            user.username = username
            user.email = area_admin.email
            if password:
                user.set_password(password)
            user.save()

        if commit:
            area_admin.save()
        return area_admin


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email', 'required': True}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject', 'required': True}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your message here...', 'required': True}),
        }
