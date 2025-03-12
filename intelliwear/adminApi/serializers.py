from rest_framework import serializers
#from django.contrib.auth.models import User
from .models import Product,Size,Media,Carousel
from django.contrib.auth.password_validation import validate_password


#product 

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file']
    
    def validate(self, data):
        product = self.context.get("product")  
        if not product and self.instance:
            product = self.instance.product 
        if product:
            media_count = Media.objects.filter(product=product).exclude(
                id=self.instance.id if self.instance else None
            ).count()
            if media_count >= 4:
                raise serializers.ValidationError("You can only upload a maximum of 4 additional media files per product.")

        return data


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'size', 'quantity']

    def validate(self, data):
        product = self.context.get("product")
        size = data.get('size')
        
        if product and Size.objects.filter(product=product, size=size).exists():
            raise serializers.ValidationError(f"Size '{size}' already exists for this product.")
        return data
    
'''
class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name' ]
'''

class ProductSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, required=False)  # Allow nested media
    sizes = SizeSerializer(many=True, required=True)   # Allow nested sizes
    #colors = ColorSerializer(many=True, required=False) # Allow nested colors
    image = serializers.ImageField(required=True, allow_null=False)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'product_type','image', 'sizes', 'media', 'gender', 'created_at', 'updated_at']

    def validate_sizes(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one size is required for the product.")
        return value
    

    def create(self, validated_data):
        try:
            media_data = validated_data.pop('media', [])
            sizes_data = validated_data.pop('sizes', [])
            #colors_data = validated_data.pop('colors', [])

            product = Product.objects.create(**validated_data)

            Media.objects.bulk_create([Media(product=product, **media) for media in media_data])

            for size in sizes_data:
                Size.objects.create(product=product, size=size['size'], quantity=size.get('quantity', 0))

        
            #color_objs = [Color.objects.get_or_create(name=color['name'])[0] for color in colors_data]
            #product.colors.set(color_objs)

            return product
        except Exception as e:
            raise serializers.ValidationError(f"Error creating product: {str(e)}")

    def update(self, instance, validated_data):
        try:
            media_data = validated_data.pop('media', [])
            sizes_data = validated_data.pop('sizes', [])
            #colors_data = validated_data.pop('colors', [])

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

            existing_sizes = {size.size: size for size in instance.sizes.all()}
            updated_sizes = []
            for size_data in sizes_data:
                size = size_data['size']
                if size in existing_sizes:
                    # Update existing size
                    existing_size = existing_sizes[size]
                    existing_size.quantity = size_data.get('quantity', 0)
                    existing_size.save()
                else:
                    # Create new size
                    Size.objects.create(product=instance, size=size, quantity=size_data.get('quantity', 0))

            # Delete sizes that were not in the update
            updated_size_names = {size['size'] for size in sizes_data}
            instance.sizes.exclude(size__in=updated_size_names).delete()

            # Fetch and update Color objects
            #color_objs = [Color.objects.get_or_create(name=color['name'])[0] for color in colors_data]
            #instance.colors.set(color_objs)

            return instance
        
        except Exception as e:
            raise serializers.ValidationError(f"Error updating product: {str(e)}")
class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'