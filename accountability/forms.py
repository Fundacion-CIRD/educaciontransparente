from django import forms

from accountability.models import Receipt, ExpenseReport


class VoucherForm(forms.ModelForm):
    expense_report = forms.ModelChoiceField(
        queryset=ExpenseReport.objects.all(),
        initial=ExpenseReport.objects.last(),
    )

    class Meta:
        model = Receipt
        fields = "__all__"
