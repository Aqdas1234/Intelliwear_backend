from rest_framework import serializers
#from django.contrib.auth.models import User
from .models import Product,Size,Media,Color,Carousel
from django.contrib.auth.password_validation import validate_password


#product 

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'media_type']
    
    def validate(self, data):
        product = self.instance.product if self.instance else data.get("product", None)

        if product:
            media_count = Media.objects.filter(product=product).exclude(id=self.instance.id if self.instance else None).count()
            if media_count >= 4:
                raise serializers.ValidationError("You can only upload a maximum of 4 additional media files per product.")

        return data


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'size']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name' ]

class ProductSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, required=False)  # Allow nested media
    sizes = SizeSerializer(many=True, required=False)   # Allow nested sizes
    colors = ColorSerializer(many=True, required=False) # Allow nested colors
    image = serializers.ImageField(required=True, allow_null=False)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description','stock', 'price', 'product_type','image', 'sizes', 'colors', 'media', 'gender', 'created_at', 'updated_at']

    def validate(self, data):
        if 'sizes' in data:
            unique_sizes = {size['size']: size for size in data['sizes']}.values()
            data['sizes'] = list(unique_sizes)  # Remove duplicates

        if 'colors' in data:
            unique_colors = {color['name']: color for color in data['colors']}.values()
            data['colors'] = list(unique_colors)  # Remove duplicates

        return data
    
    def create(self, validated_data):
        media_data = validated_data.pop('media', [])
        sizes_data = validated_data.pop('sizes', [])
        colors_data = validated_data.pop('colors', [])

        product = Product.objects.create(**validated_data)

        # Bulk create Media objects
        Media.objects.bulk_create([Media(product=product, **media) for media in media_data])

        # Fetch existing sizes and colors or create new ones
        size_objs = [Size.objects.get_or_create(size=size['size'])[0] for size in sizes_data]
        product.sizes.set(size_objs)

        color_objs = [Color.objects.get_or_create(name=color['name'])[0] for color in colors_data]
        product.colors.set(color_objs)

        return product


    def update(self, instance, validated_data):
        media_data = validated_data.pop('media', [])
        sizes_data = validated_data.pop('sizes', [])
        colors_data = validated_data.pop('colors', [])

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update media efficiently
        existing_media_ids = set(instance.media.values_list('id', flat=True))
        new_media = []
        for media in media_data:
            if 'id' in media and media['id'] in existing_media_ids:
                existing_media_ids.remove(media['id'])  # Keep existing media
            else:
                new_media.append(Media(product=instance, **media))  # Add new media

        # Remove media that was not in the update
        Media.objects.filter(id__in=existing_media_ids).delete()
        Media.objects.bulk_create(new_media)

        # Fetch and update Size objects
        size_objs = [Size.objects.get_or_create(size=size['size'])[0] for size in sizes_data]
        instance.sizes.set(size_objs)

        # Fetch and update Color objects
        color_objs = [Color.objects.get_or_create(name=color['name'])[0] for color in colors_data]
        instance.colors.set(color_objs)

        return instance

class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'