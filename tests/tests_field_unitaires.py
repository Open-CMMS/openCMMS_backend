from django.test import TestCase
from maintenancemanagement.models import Field, FieldGroup


class FieldTests(TestCase):

    def set_up_fieldgroup(self):
        """
            Set-up FieldGroup for the tests
        """
        fieldGroup = FieldGroup.objects.create(name="truc", is_equipment=False)
        return fieldGroup

    def test_field_create(self):
        """
            Test the creation of a Field with field_group
        """
        fieldGroup = self.set_up_fieldgroup()
        field = Field(name="Machin", field_group=fieldGroup)
        self.assertEqual(field.name, "Machin")
        self.assertEqual(field.field_group, fieldGroup)

    def test_field_with_save(self):
        """
            Test the saving of a FieldGroup in the database.
        """
        fieldGroup = self.set_up_fieldgroup()
        unFieldGroup = FieldGroup.objects.create(name="unFieldGroup", is_equipment=True)
        field = Field(name="Machin", field_group=fieldGroup)
        field.save()
        unField = Field.objects.create(name="unField", field_group=unFieldGroup)
        self.assertEqual(field, Field.objects.get(name="Machin"))
        self.assertEqual(unField, Field.objects.get(name="unField"))
