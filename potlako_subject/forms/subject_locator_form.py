from django import forms
from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidatorMixin
from edc_locator.forms import (
    SubjectLocatorFormValidator as BaseSubjectLocatorFormValidator)

from ..models import SubjectLocator


class SubjectLocatorFormValidator(BaseSubjectLocatorFormValidator):

    def validate_indirect_contact(self):
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_name')
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_relation')
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_cell')
        for field in ['indirect_contact_cell_alt', 'indirect_contact_phone']:
            self.not_required_if(
                NO, field='may_contact_indirectly', field_required=field,
                inverse=False)

    def clean(self):
        super().clean()
        for field in ['mail_address', 'physical_address']:
            self.required_if(
                YES, field='may_visit_home',
                field_required=field)

        for field in ['alt_contact_name', 'alt_contact_rel']:
            self.required_if(
                YES, field='has_alt_contact',
                field_required=field)

        alt_contact_cell = self.cleaned_data.get('alt_contact_cell')
        alt_contact_tel = self.cleaned_data.get('alt_contact_tel')

        if alt_contact_cell == '' and alt_contact_tel == '':
            message = {'alt_contact_cell':
                           'A cell number or',
                       'alt_contact_tel':
                           'telephone number is required'}
            self._errors.update(message)
            raise ValidationError(message)

        for field in ['other_alt_contact_cell', 'alt_contact_tel']:
            self.not_required_if(
                NO, field='has_alt_contact', field_required=field,
                inverse=False)

        self.required_if(
            YES, field='may_call',
            field_required='subject_cell')

        self.not_required_if(
            NO, field='may_contact_indirectly',
            field_required='has_alt_contact',
            not_required_msg='This person should be the next of kin above.')


class SubjectLocatorForm(FormValidatorMixin, forms.ModelForm):

    form_validator_cls = SubjectLocatorFormValidator

    subject_identifier = forms.CharField(
        label='Subject Identifier',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = SubjectLocator
        fields = '__all__'
