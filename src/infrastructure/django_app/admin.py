from django.contrib import admin

from .models import AgentRoleModel, ProjectModel, RunLogModel, SkillModel, TeamMemberModel


class SkillInline(admin.TabularInline):
    model = SkillModel
    extra = 0


@admin.register(AgentRoleModel)
class AgentRoleAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "mode")
    inlines = [SkillInline]


class TeamMemberInline(admin.TabularInline):
    model = TeamMemberModel
    extra = 0


@admin.register(ProjectModel)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "created_at")
    inlines = [TeamMemberInline]


@admin.register(RunLogModel)
class RunLogAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "started_at", "finished_at")
    list_filter = ("status",)
