from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from application.use_cases.build_team import build_team
from application.use_cases.generate_project import generate_project
from application.use_cases.start_run import start_run
from domain.exceptions import DomainError
from domain.value_objects import slugify_strict
from infrastructure import container
from infrastructure.django_app.models import ProjectModel, RunLogModel

from .forms import TeamBuilderForm


def builder(request):
    role_repo = container.agent_role_repo()
    roles = role_repo.list_all()
    role_choices = [(role.slug, f"{role.name} — {role.description}") for role in roles]

    if request.method == "POST":
        form = TeamBuilderForm(request.POST, role_choices=role_choices)
        if form.is_valid():
            slug = slugify_strict(form.cleaned_data["project_name"])
            try:
                build_team(
                    container.project_repo(),
                    container.team_repo(),
                    role_repo,
                    slug=slug,
                    name=form.cleaned_data["project_name"],
                    brief=form.cleaned_data["brief"],
                    output_root=settings.GENERATED_TEAMS_ROOT,
                    member_role_slugs=form.cleaned_data["roles"],
                )
                generate_project(
                    container.project_repo(),
                    container.team_repo(),
                    role_repo,
                    container.scaffold_writer(),
                    project_slug=slug,
                )
                messages.success(request, f'Generated "{form.cleaned_data["project_name"]}".')
                return redirect("dashboard", slug=slug)
            except DomainError as exc:
                form.add_error(None, str(exc))
    else:
        form = TeamBuilderForm(role_choices=role_choices)

    return render(request, "web/builder.html", {"form": form, "roles": roles})


def dashboard(request, slug):
    project_row = get_object_or_404(ProjectModel, slug=slug)

    if request.method == "POST" and request.POST.get("action") == "start_run":
        start_run(
            container.project_repo(),
            container.event_publisher(),
            container.run_log_repo(),
            project_slug=slug,
        )
        return redirect("dashboard", slug=slug)

    team = container.team_repo().get_for_project(slug)
    tracking = _read_tracking(project_row.output_path)
    run_logs = RunLogModel.objects.filter(project=project_row)[:10]

    return render(
        request,
        "web/dashboard.html",
        {"project": project_row, "team": team, "tracking": tracking, "run_logs": run_logs},
    )


def dashboard_tasks_partial(request, slug):
    project_row = get_object_or_404(ProjectModel, slug=slug)
    tracking = _read_tracking(project_row.output_path)
    run_log = container.run_log_repo().latest_for_project(slug)
    return render(request, "web/_tasks.html", {"tracking": tracking, "run_log": run_log})


def _read_tracking(output_path: str) -> dict | None:
    path = Path(output_path) / "tracking.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
