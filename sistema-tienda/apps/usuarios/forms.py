from django import forms
from .models import Usuario

class RegistroUsuarioForm(forms.ModelForm):
    # Campo de contraseña manual (para que no se muestre en texto plano)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-form', 'placeholder': 'Contraseña segura'}),
        label="Contraseña temporal"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'password', 'rol', 'sede']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input-form', 'placeholder': 'Ej. jmanuel'}),
            'first_name': forms.TextInput(attrs={'class': 'input-form', 'placeholder': 'Nombre del empleado'}),
            'last_name': forms.TextInput(attrs={'class': 'input-form', 'placeholder': 'Apellido del empleado'}),
            'rol': forms.Select(attrs={'class': 'input-form'}),
            'sede': forms.Select(attrs={'class': 'input-form'}),
        }

    def save(self, commit=True):
        # Interceptamos el guardado para cifrar la clave antes de inyectarla en PostgreSQL
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'rol', 'sede', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input-form', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'input-form'}),
            'last_name': forms.TextInput(attrs={'class': 'input-form'}),
            'rol': forms.Select(attrs={'class': 'input-form'}),
            'sede': forms.Select(attrs={'class': 'input-form'}),
            'is_active': forms.CheckboxInput(attrs={'style': 'width: 20px; height: 20px; cursor: pointer;'}),
        }
        labels = {
            'is_active': 'Usuario Activo (Desmarca esta casilla para suspender el acceso)'
        }