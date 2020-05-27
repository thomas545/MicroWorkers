import os
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import views, viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Transaction
from users.models import Skill


class TransactionView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        callback func for payment
        """
        pass

    def post(self, request, *args, **kwargs):
        """
        client complete payment after tasker accept task
        """

        total_amount = 0
        payment_fees = 5
        transaction = get_object_or_404(Transaction, pk=request.data.get('transaction', None))
        if transaction.task_deal.task.client != request.user:
            raise PermissionDenied(_("Transaction not belong to you"))
        tasker_skill = Skill.objects.filter(tasker=transaction.task_deal.tasker, 
                                        skill=transaction.task_deal.task.category)
        task_rate = tasker_skill.first.rate_per_hour * transaction.task_deal.task.duration_time
        our_fees = (os.environ.get('OUR_FEES') / 100) * task_rate
        total_amount += our_fees + payment_fees + task_rate
        # TODO Payment integration, encrypt our_transaction_id in payment process and save it
        transaction.our_transaction_id = str(transaction.id)
        transaction.payment_id = "123"
        transaction.payment_fees = payment_fees
        transaction.our_fees = our_fees
        transaction.total_amount = total_amount
        transaction.save()
        # TODO redirect to call back
        return Response("detail": _("Complete transaction process ..."))