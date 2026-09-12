from django.db import models


class AgentRoleModel(models.Model):
    slug = models.SlugField(primary_key=True, max_length=64)
    name = models.CharField(max_length=100)
    description = models.TextField()
    mode = models.CharField(max_length=20)
    guidelines_md = models.TextField()

    class Meta:
        db_table = "agent_role"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class SkillModel(models.Model):
    role = models.ForeignKey(AgentRoleModel, related_name="skills", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=64)
    name = models.CharField(max_length=100)
    description = models.TextField()
    content_md = models.TextField()

    class Meta:
        db_table = "skill"
        unique_together = ("role", "slug")
        ordering = ["role_id", "name"]

    def __str__(self) -> str:
        return f"{self.role_id}/{self.slug}"


class ProjectModel(models.Model):
    slug = models.SlugField(primary_key=True, max_length=80)
    name = models.CharField(max_length=200)
    brief = models.TextField()
    output_path = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class TeamMemberModel(models.Model):
    project = models.ForeignKey(ProjectModel, related_name="members", on_delete=models.CASCADE)
    role = models.ForeignKey(AgentRoleModel, on_delete=models.PROTECT)

    class Meta:
        db_table = "team_member"
        unique_together = ("project", "role")


class RunLogModel(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested"
        RUNNING = "running"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    project = models.ForeignKey(ProjectModel, related_name="run_logs", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    log_tail = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "run_log"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.project_id} [{self.status}]"
