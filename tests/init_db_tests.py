from maintenancemanagement.models import (
    Equipment,
    EquipmentType,
    Field,
    FieldGroup,
    FieldObject,
    FieldValue,
    Task,
)
from utils.models import Plugin


def init_db():
    field_gr_cri_dec = FieldGroup.objects.create(name="Trigger Conditions", is_equipment=False)
    Field.objects.create(name="Date", field_group=field_gr_cri_dec)
    Field.objects.create(name="Integer", field_group=field_gr_cri_dec)
    Field.objects.create(name="Float", field_group=field_gr_cri_dec)
    Field.objects.create(name="Duration", field_group=field_gr_cri_dec)
    field_recurrence_dec = Field.objects.create(name="Recurrence", field_group=field_gr_cri_dec)

    FieldValue.objects.create(value="Day", field=field_recurrence_dec)
    FieldValue.objects.create(value="Week", field=field_recurrence_dec)
    FieldValue.objects.create(value="Month", field=field_recurrence_dec)
    FieldValue.objects.create(value="Year", field=field_recurrence_dec)

    field_gr_cri_fin = FieldGroup.objects.create(name="End Conditions", is_equipment=False)

    Field.objects.create(name="Checkbox", field_group=field_gr_cri_fin)
    Field.objects.create(name="Integer", field_group=field_gr_cri_fin)
    Field.objects.create(name="Description", field_group=field_gr_cri_fin)
    Field.objects.create(name="Photo", field_group=field_gr_cri_fin)

    field_gr_test = FieldGroup.objects.create(name='FieldGroupTest')
    Field.objects.create(name="FieldWithoutValueTest", field_group=field_gr_test)
    field_with_value = Field.objects.create(name="FieldWithValueTest", field_group=field_gr_test)
    FieldValue.objects.create(value="FieldValueTest", field=field_with_value)
    equip_type = EquipmentType.objects.create(name='EquipmentTypeTest')
    equip_type.fields_groups.add(field_gr_test)
    Task.objects.create(name='TemplateTest', duration='2d', is_template=True, equipment_type=equip_type)

    embouteilleuse_field_gr = FieldGroup.objects.create(name='EmbouteilleuseFieldGroup')
    pression = Field.objects.create(name="Pression", field_group=embouteilleuse_field_gr)
    nb_bouteilles = Field.objects.create(name="Nb bouteilles", field_group=embouteilleuse_field_gr)
    marque = Field.objects.create(name="Marque", field_group=embouteilleuse_field_gr)
    gai = FieldValue.objects.create(value="GAI", field=marque)
    bosh = FieldValue.objects.create(value="BOSH", field=marque)
    embouteilleuse = EquipmentType.objects.create(name='Embouteilleuse')
    embouteilleuse.fields_groups.add(embouteilleuse_field_gr)
    embouteilleuse_axb1 = Equipment.objects.create(name="Embouteilleuse AXB1", equipment_type=embouteilleuse)
    pression_object = FieldObject.objects.create(described_object=embouteilleuse_axb1, field=pression, value="1.012")
    FieldObject.objects.create(described_object=embouteilleuse_axb1, field=nb_bouteilles, value="50000")
    FieldObject.objects.create(described_object=embouteilleuse_axb1, field=marque, field_value=gai)
    Plugin.objects.create(
        file_name="fichier_test_plugin.py",
        ip_address="127.0.0.1",
        equipment=embouteilleuse_axb1,
        field_object=pression_object,
        recurrence="30d"
    )
