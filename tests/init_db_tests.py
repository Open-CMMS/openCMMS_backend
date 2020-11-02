from maintenancemanagement.models import (
    EquipmentType,
    Field,
    FieldGroup,
    FieldValue,
    Task,
)


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

    equip_type = EquipmentType.objects.get(name='EquipmentTypeTest')
    Task.objects.create(name='TemplateTest', duration='2d', is_template=True, equipment_type=equip_type)
