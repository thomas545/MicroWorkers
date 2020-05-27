from django.db import models
from base.models import TimeStampedModel
from tasks.models import TaskDeal


class Transaction(TimeStampedModel):
    task_deal = models.ForeignKey(
        TaskDeal, related_name="deal_transaction", on_delete=models.CASCADE
    )
    payment_id = models.CharField(max_length=250, blank=True, null=True)
    our_transaction_id = models.CharField(max_length=250, blank=True, null=True)
    payment_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    our_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"Transaction ({self.id})"
