from django.contrib import admin
from .models import Chambre, ChambreImage, GalerieImage, GalerieItem


class ChambreImageInline(admin.TabularInline):
    model = ChambreImage
    extra = 1

@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ['numero', 'type', 'prix', 'disponible']
    list_filter = ['type', 'disponible']
    search_fields = ['numero']
    inlines = [ChambreImageInline]

@admin.register(ChambreImage)
class ChambreImageAdmin(admin.ModelAdmin):
    list_display = ['chambre', 'image']


class GalerieImageInline(admin.TabularInline):
    model = GalerieImage
    extra = 3
    fields = ['image', 'description', 'ordre']


@admin.register(GalerieItem)
class GalerieItemAdmin(admin.ModelAdmin):
    list_display = ['titre', 'actif', 'nombre_images', 'ordre', 'created_at']
    list_filter = ['actif', 'created_at']
    search_fields = ['titre', 'description']
    inlines = [GalerieImageInline]

    def nombre_images(self, obj):
        return obj.images.count()

    nombre_images.short_description = 'Nombre d\'images'