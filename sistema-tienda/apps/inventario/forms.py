from django import forms

from apps.usuarios.models import Sede

from .models import Categoria, ProductoInventario


FORM_INPUT_CLASS = (
    'mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 '
    'text-slate-900 shadow-sm outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200'
)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': FORM_INPUT_CLASS,
                'placeholder': 'Ej. Bebidas',
            }),
        }

    def clean_nombre(self):
        return self.cleaned_data['nombre'].strip()


class ProductoInventarioForm(forms.ModelForm):
    class Meta:
        model = ProductoInventario
        fields = ['nombre', 'categoria', 'cantidad', 'precio', 'foto', 'sede']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': FORM_INPUT_CLASS,
                'placeholder': 'Nombre del producto',
            }),
            'categoria': forms.Select(attrs={'class': FORM_INPUT_CLASS}),
            'cantidad': forms.NumberInput(attrs={
                'class': FORM_INPUT_CLASS,
                'min': 0,
                'step': 1,
            }),
            'precio': forms.NumberInput(attrs={
                'class': FORM_INPUT_CLASS,
                'min': 0,
                'step': '0.01',
            }),
            'foto': forms.ClearableFileInput(attrs={'class': FORM_INPUT_CLASS}),
            'sede': forms.Select(attrs={'class': FORM_INPUT_CLASS}),
        }

    def __init__(self, *args, sedes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.order_by('nombre')
        self.fields['sede'].queryset = sedes if sedes is not None else Sede.objects.filter(activa=True)

    def clean_nombre(self):
        return self.cleaned_data['nombre'].strip()

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad < 0:
            raise forms.ValidationError('La cantidad no puede ser negativa.')
        return cantidad

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio
