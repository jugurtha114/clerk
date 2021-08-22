from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import Http404


from case.forms import (
    DynamicTableForm,
    ClientContactDynamicForm,
    ClientMiscDynamicForm,
    ClientPersonalDynamicForm,
    TenancyDynamicForm,
    PersonDynamicForm,
)
from core.models import Client, Tenancy, Person, Issue

from .auth import paralegal_or_better_required

CLIENT_DETAIL_FORMS = {
    "contact": ClientContactDynamicForm,
    "personal": ClientPersonalDynamicForm,
    "misc": ClientMiscDynamicForm,
}

TENANCY_DETAIL_FORMS = {
    "form": TenancyDynamicForm,
}

PERSON_DETAIL_FORMS = {
    "form": PersonDynamicForm,
}


@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def client_detail_view(request, pk, form_slug: str = ""):
    try:
        client = Client.objects.prefetch_related("issue_set").get(pk=pk)
        if request.user.is_paralegal:
            is_assigned = Issue.objects.filter(
                client=client, paralegal=request.user
            ).exists()
            if not is_assigned:
                # Not allowed
                raise Http404()

    except Client.DoesNotExist:
        raise Http404()

    forms = DynamicTableForm.build_forms(
        request, form_slug, client, CLIENT_DETAIL_FORMS
    )
    context = {"client": client, "forms": forms}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/client_detail.html", context)


@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def tenancy_detail_view(request, pk, form_slug: str = ""):
    try:
        tenancy = Tenancy.objects.get(pk=pk)
        if request.user.is_paralegal:
            is_assigned = Issue.objects.filter(
                client=tenancy.client, paralegal=request.user
            ).exists()
            if not is_assigned:
                # Not allowed
                raise Http404()

    except Tenancy.DoesNotExist:
        raise Http404()

    forms = DynamicTableForm.build_forms(
        request, form_slug, tenancy, TENANCY_DETAIL_FORMS
    )
    context = {"tenancy": tenancy, "forms": forms}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/tenancy_detail.html", context)


@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def person_detail_view(request, pk, form_slug: str = ""):
    try:
        # FIXME: Limit access to only paralegals who are assigned to cases where
        # There people are involved.
        person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        raise Http404()

    forms = DynamicTableForm.build_forms(
        request, form_slug, person, PERSON_DETAIL_FORMS
    )
    context = {"person": person, "forms": forms}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/person_detail.html", context)
