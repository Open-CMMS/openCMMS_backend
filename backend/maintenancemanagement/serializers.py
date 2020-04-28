from .models import Equipment, EquipmentType
"""
Serializers enable the link between front-end and back-end
"""

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = [id, name, equipment_type]
        #ajouter les fichiers par la suite

class EquipmentTypeSerializer(serializer.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = [id, name, field]
