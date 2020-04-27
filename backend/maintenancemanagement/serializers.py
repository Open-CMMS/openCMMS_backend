"""
Serializers enable the link between front-end and back-end
"""

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = [id, name, equipment_type]
        #ajouter les fichiers par la suite
