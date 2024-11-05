from typing import Any
from django.db import models
from stock.models import Stock
from decimal import Decimal
from django.core.validators import RegexValidator
from django.db.models import Sum
from django.contrib.auth.models import User

# Abstract Commun Class
class Commun(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now=True)

    @property
    def get_TTC(self):
        """Total price with tax (20% VAT)."""
        return round(self.get_HT * Decimal(1.20), 2)

    @property
    def get_TVA(self):
        """Calculate the 20% VAT from the HT price."""
        tva = self.get_HT * Decimal(0.2)
        return round(tva, 2)

    class Meta:
        abstract = True

# Sale Model
class Sale(Commun):
    @property
    def get_HT(self):
        """Calculate the total price without tax for all order lines."""
        return sum(order.get_subtotal for order in self.order_line_set.all())

    @property
    def total_of_items(self):
        """Get the total number of items in this sale."""
        return self.order_line_set.count()

    def __str__(self):
        return f"SO{self.pk}"
class SaleToPersone(Sale):
    pass
# Refund Model
class Refund(Commun):
    CAT_CHOICES = [
        ('ERROR','ERROR'),
        ('DEFECTIVE','DEFECTIVE')
    ]
    so = models.CharField(max_length=30)
    sale = models.OneToOneField(Sale, on_delete=models.PROTECT, null=True, blank=True)  # One-to-one relationship with Sale
    reason = models.CharField(max_length=10,choices=CAT_CHOICES)
    @property
    def get_HT(self):
        """Calculate the total price without tax for all return lines."""
        return sum(order.get_subtotal for order in self.refund_line_set.all())

    @property
    def total_of_items(self):
        """Get the total number of items in this refund."""
        return self.refund_line_set.count()

    def __str__(self):
        return f"Refund {self.pk}"

# Devis Model
class Devis(Commun):
    customer = models.CharField(max_length=30)

    @property
    def get_HT(self):
        """Calculate the total price without tax for all devis lines."""
        return sum(order.get_subtotal for order in self.devis_line_set.all())

    @property
    def total_of_items(self):
        """Get the total number of items in this devis."""
        return self.devis_line_set.count()

    def __str__(self):
        return f"Devis {self.pk}"

# Abstract LineItem Model
class LineItem(models.Model):
    item = models.ForeignKey(Stock, on_delete=models.PROTECT)
    description = models.CharField(max_length=30)
    quantity = models.PositiveIntegerField()  # Ensure only positive quantities
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def get_subtotal(self):
        """Calculate the subtotal for this line."""
        return Decimal(self.quantity) * Decimal(self.price)

    @property
    def quantity_by_crtn(self):
        """Calculate how many cartons and units."""
        cartons = self.quantity // self.item.qte_by_carton
        units = self.quantity % self.item.qte_by_carton
        return f"{cartons} cartons | {units} units"

    def save(self, *args, **kwargs):
        """Auto-populate description based on the associated item."""
        if self.item:
            self.description = self.item.item.description
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
# Inline Order, Devis, and Refund Lines
class Order_Line(LineItem):
    sale = models.ForeignKey(Sale, on_delete=models.DO_NOTHING)


class Devis_Line(LineItem):
    devis = models.ForeignKey(Devis, on_delete=models.DO_NOTHING)


class Refund_Line(LineItem):
    refund = models.ForeignKey(Refund, on_delete=models.DO_NOTHING)
    
# Dealer Model
class Dealer(models.Model):
    created_at = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=100)
    phone_whatsapp = models.CharField(
        max_length=13,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,13}$',
            message="Phone number must be entered in the format: '+212**********'. Up to 13 digits allowed.")]
    )
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    @property
    def get_balance(self):
        return self.balance
    @get_balance.setter
    def get_balance(self,value):
        self.balance = value
    @property
    def count_sales(self):
        return self.sales.count()    
    @property
    def total_sales(self):
        """Calculate total sales for the dealer."""
        return sum(sale.get_TTC for sale in self.sales.all())

    @property
    def last_payment_date(self):
        """Get the date of the last payment made by the dealer."""
        payments = MonthlyPayment.objects.filter(dealer=self).order_by('-date')
        return payments.first().date if payments.exists() else None
    @property
    def get_partial_and_unpaid_sales(self):
        """
        Retrieves all sales for the given dealer that are either unpaid or partially paid.
        Sales are ordered by date (oldest first).
        """
        # Get all sales for the dealer, ordered by date
        sales = SaleToDealer.objects.filter(dealer=self).order_by('date')

        # Filter for unpaid and partially paid sales in Python
        unpaid_sales = [sale for sale in sales if sale.amount_due > 0]

        return unpaid_sales
    @property
    def total_unpaid(self):
        sales = self.get_partial_and_unpaid_sales
        total_unpaid = sum(
                sale.get_TTC - sum(payment.amount_paid for payment in sale.sale_payments.all())
                for sale in sales
            )
        return total_unpaid
        

    def get_total_paid(self):
        """Calculate the total amount paid by the dealer."""
        total_paid = self.sales.annotate(
            total_sale_payment=Sum('sale_payments__amount_paid')
        ).aggregate(total=Sum('total_sale_payment'))['total'] or 0
        return total_paid

    def __str__(self):
        return f"{self.name}"

# SaleToDealer Model
class SaleToDealer(Sale):
    dealer = models.ForeignKey(Dealer,related_name='sales', on_delete=models.PROTECT)
    @property
    def amount_due(self):
        """Calculate the amount still due for this sale."""
        total_paid = sum(payment.amount_paid for payment in self.sale_payments.all())
        return self.get_TTC - total_paid
    @property
    def remaining_balance(self):
        """Calculate the remaining balance for this sale."""
        return self.get_TTC - self.total_paid

    @property
    def is_fully_paid(self):
        """Check if the sale is fully paid."""
        return self.remaining_balance <= 0
    @property
    def adjust_total_for_refund(self, amount):
        """Adjust the total amount of the sale for a refund."""
        self.total_amount -= amount
        self.save()
    def __str__(self):
        return f"Sale ID:{self.pk},Dealer:{self.dealer}"
# RefundFromDealer Model
class RefundFromDealer(Refund):
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT)

    def process_refund(self):
        """Process a refund by adjusting the sale and updating payments."""
        self.sale.adjust_total_for_refund(self.amount_refunded)
        sale_payment = SalePayment.objects.get(sale=self.sale)
        sale_payment.update_payment_after_refund(self.amount_refunded)

    def __str__(self):
        return f"Refund {self.pk} from {self.dealer.name}"


# Payment Models
class Payment(models.Model):
    """Base class for all payments."""
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)

# Cash Payment Subclass
class CashPayment(Payment):
    cash_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def get_change(self):
        """Calculate the change to be returned."""
        return round(self.cash_received - self.amount, 2)

    def __str__(self):
        return f"Cash Payment of {self.amount}"

# Monthly Payment Subclass
class MonthlyPayment(Payment):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT)
    
    def save(self, *args, **kwargs):
        self.dealer.balance -= self.amount
        self.dealer.save()
        super().save(*args, **kwargs)

# RefundPyment Subclass
class RefundPayment(Payment):
    pass
# Sale Payment Model
class SalePayment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='sale_payments')
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='sale_payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    @property
    def get_amount_paid(self):
        return self.amount_paid
    @get_amount_paid.setter
    def get_amount_paid(self, value):
        self.amount_paid = value

    def update_payment_after_refund(self, amount_refunded):
        """Update the payment record after a refund."""
        self.amount_paid -= amount_refunded
        self.save()

    def __str__(self):
        return f"Payment for {self.sale} - Amount Paid: {self.amount_paid}"

# Refund From Dealer
class RefundDealerPayment(Payment):
    pass
# Refund Normal from a person 
class RefundNormal(Refund):
    pass