class DomainError(Exception):
    """Base class for all domain-level errors."""


class UnknownRoleError(DomainError):
    def __init__(self, slug: str):
        super().__init__(f"unknown agent role: {slug!r}")
        self.slug = slug


class UnknownProjectError(DomainError):
    def __init__(self, slug: str):
        super().__init__(f"unknown project: {slug!r}")
        self.slug = slug


class ProjectAlreadyExistsError(DomainError):
    def __init__(self, slug: str):
        super().__init__(f"project already exists: {slug!r}")
        self.slug = slug


class EmptyTeamError(DomainError):
    def __init__(self) -> None:
        super().__init__("a team needs at least one agent role")


class ScaffoldWriteError(DomainError):
    """Raised when the output project folder cannot be written."""
