from django import forms
from django.forms.fields import BooleanField
from django.contrib.auth.models import Group
from django.db import transaction

from accounts.models import User, CaseGroups
from core.models import Issue, IssueNote, Client, Tenancy, Person
from core.models.issue import CaseStage
from emails.models import Email, EmailState, EmailAttachment
from case.utils import DynamicTableForm, MultiChoiceField, SingleChoiceField


class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = [
            "from_address",
            "to_address",
            "cc_addresses",
            "subject",
            "state",
            "text",
            "issue",
            "sender",
        ]

    subject = forms.CharField()
    to_address = forms.EmailField()
    attachments = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False
    )

    @transaction.atomic
    def save(self, commit=True):
        email = super().save()
        for f in self.files.getlist("attachments"):
            EmailAttachment.objects.create(
                email=email,
                file=f,
                content_type=f.content_type,
            )
        return email


class PersonDynamicForm(DynamicTableForm):
    class Meta:
        model = Person
        fields = [
            "full_name",
            "email",
            "address",
            "phone_number",
        ]


class TenancyDynamicForm(DynamicTableForm):
    class Meta:
        model = Tenancy
        fields = [
            "address",
            "suburb",
            "postcode",
            "started",
            "is_on_lease",
        ]

    is_on_lease = SingleChoiceField(field_name="is_on_lease", model=Tenancy)


class ClientPersonalDynamicForm(DynamicTableForm):
    class Meta:
        model = Client
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
        ]


class ClientContactDynamicForm(DynamicTableForm):
    class Meta:
        model = Client
        fields = [
            "email",
            "phone_number",
            "call_times",
        ]

    call_times = MultiChoiceField("call_times", Client)


class ClientMiscDynamicForm(DynamicTableForm):
    class Meta:
        model = Client
        fields = [
            "referrer",
            "referrer_type",
            "employment_status",
            "special_circumstances",
            "weekly_income",
            "primary_language",
            "number_of_dependents",
            "is_aboriginal_or_torres_strait_islander",
            "legal_access_difficulties",
            "rental_circumstances",
            "weekly_rent",
            "is_multi_income_household",
        ]

    rental_circumstances = SingleChoiceField(
        field_name="rental_circumstances", model=Client
    )
    referrer_type = SingleChoiceField(field_name="referrer_type", model=Client)
    employment_status = MultiChoiceField("employment_status", Client)
    special_circumstances = MultiChoiceField("special_circumstances", Client)
    legal_access_difficulties = MultiChoiceField("legal_access_difficulties", Client)


class ParalegalNoteForm(forms.ModelForm):
    class Meta:
        model = IssueNote
        fields = [
            "issue",
            "creator",
            "note_type",
            "text",
        ]

    text = forms.CharField(label="Paralegal note", min_length=1, max_length=2048)


class CaseReviewNoteForm(forms.ModelForm):
    class Meta:
        model = IssueNote
        fields = [
            "issue",
            "creator",
            "note_type",
            "text",
            "event",
        ]

    text = forms.CharField(label="Review note", min_length=1, max_length=2048)
    event = forms.DateField(label="Next review date", required=True)


class ParalegalReviewNoteForm(forms.ModelForm):
    class Meta:
        model = IssueNote
        fields = [
            "issue",
            "creator",
            "note_type",
            "text",
        ]

    text = forms.CharField(label="Review note", min_length=1, max_length=2048)


class UserDetailsDynamicForm(DynamicTableForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "is_intern",
        ]


class UserPermissionsDynamicForm(DynamicTableForm):
    class Meta:
        model = User
        fields = []

    def __init__(self, requesting_user, instance, *args, **kwargs):
        # Figure out which groups the requesting user is allowed to edit.
        self.editable_groups = []
        if requesting_user.is_admin_or_better:
            self.editable_groups = [CaseGroups.COORDINATOR, CaseGroups.PARALEGAL]
        elif requesting_user.is_coordinator:
            self.editable_groups = [CaseGroups.PARALEGAL]

        # Figure out which groups the target user currently has
        target_user = instance
        target_user_groups = target_user.groups.filter(
            name__in=CaseGroups.GROUPS
        ).values_list("pk", flat=True)
        initial = {}
        extra_fields = {}
        for group in Group.objects.filter(name__in=CaseGroups.GROUPS):
            field_name = self.get_group_field_name(group.name)
            initial[field_name] = group.pk in target_user_groups
            is_readonly = group.name not in self.editable_groups
            extra_fields[field_name] = forms.BooleanField(
                disabled=is_readonly, required=False
            )

        super().__init__(*args, initial=initial, instance=instance, **kwargs)
        self.fields.update(extra_fields)
        super().set_display_values()

    @staticmethod
    def get_display_value(field, bound_field):
        return "True" if bound_field.value() else "False"

    def get_group_field_name(self, group_name):
        return "has_" + group_name.lower() + "_permissions"

    def clean(self):
        super().clean()
        allowed_field_names = [
            self.get_group_field_name(gn) for gn in self.editable_groups
        ]
        self.cleaned_data = {
            k: v for k, v in self.cleaned_data.items() if k in allowed_field_names
        }

    def save(self):
        user = self.instance
        # This does a bunch of queries and I don't care.
        for group in Group.objects.filter(name__in=CaseGroups.GROUPS):
            if group.name not in self.editable_groups:
                continue

            user_has_group = user.groups.filter(pk=group.pk).exists()
            field_name = self.get_group_field_name(group.name)
            is_group_selected = self.cleaned_data[field_name]
            if user_has_group and not is_group_selected:
                # Remove group
                user.groups.remove(group)
            elif is_group_selected and not user_has_group:
                # Add group
                user.groups.add(group)


class IssueSearchForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "topic",
            "stage",
            "outcome",
            "provided_legal_services",
            "is_open",
        ]

    def search(self, issue_qs):
        for k, v in self.data.items():
            if k not in self.fields:
                continue

            if type(self.fields[k]) is BooleanField:
                is_field_valid = v in ["True", "False"]
                filter_value = v == "True"
            else:
                is_field_valid = self.fields[k].valid_value(v)
                filter_value = v

            if is_field_valid:
                issue_qs = issue_qs.filter(**{k: filter_value})

        return issue_qs


class IssueProgressForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "stage",
            "provided_legal_services",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stage_field = self.fields["stage"]
        filtered_choices = []
        for choice in stage_field._choices:
            if choice[0] != "CLOSED":
                filtered_choices.append(choice)

        stage_field._choices = filtered_choices


class IssueOutcomeForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "outcome",
            "outcome_notes",
            "provided_legal_services",
        ]


class IssueCloseForm(IssueOutcomeForm):
    def save(self, commit=True):
        self.instance.is_open = False
        self.instance.stage = CaseStage.CLOSED
        super().save(commit=False)
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()


class IssueReOpenForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["stage"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stage_field = self.fields["stage"]
        filtered_choices = []
        for choice in stage_field._choices:
            if choice[0] != "CLOSED":
                filtered_choices.append(choice)

        stage_field._choices = filtered_choices

    def save(self, commit=True):
        self.instance.is_open = True
        super().save(commit=False)
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()


class IssueAssignParalegalForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["paralegal"]
