from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import Http404

from case.forms import (
    DynamicTableForm,
    ClientContactDynamicForm,
    ClientMiscDynamicForm,
    ClientPersonalDynamicForm,
)
from core.models import Client, Issue
from .auth import paralegal_or_better_required
from case.utils.router import Router

CLIENT_DETAIL_FORMS = {
    "contact": ClientContactDynamicForm,
    "personal": ClientPersonalDynamicForm,
    "misc": ClientMiscDynamicForm,
}

router = Router("client")
router.create_route("detail").uuid("pk").slug("form_slug", optional=True)


@router.use_route("detail")
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
