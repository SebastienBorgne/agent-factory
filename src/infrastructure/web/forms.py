from django import forms


class TeamBuilderForm(forms.Form):
    project_name = forms.CharField(
        max_length=200,
        label="Project name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Acme Order Tracker"}),
    )
    brief = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "Describe what you want built. Mention a tech stack if you have "
                "one in mind — otherwise the team will pick and record one.",
            }
        ),
        label="Project brief",
    )
    roles = forms.MultipleChoiceField(choices=(), widget=forms.CheckboxSelectMultiple, label="Team")

    def __init__(self, *args, role_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["roles"].choices = role_choices
