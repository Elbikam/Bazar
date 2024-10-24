
from django.test import TestCase
from django.urls import reverse
from sale.models import Sale, Order_Line, CashPayment, SalePayment
from sale.forms import SaleForm, OrderFormSet, CashPaymentForm
from stock.models import Item, Stock
from decimal import Decimal

class SaleCreateViewTests(TestCase):
    def setUp(self):
        # Create necessary test data
        i = Item.objects.create(
            id=111,
            name='Test Item',
            category='Test Category',
            description='Test description',
            price=100
        )
        self.item = Stock.objects.create(item=i, get_current_qte=10)

    def test_post_request_successful_sale_creation(self):
        sale_data = {
            'date': '2024-10-24 11:48:33.655979',  # Example date; adjust as necessary
        }
    
        order_data = {
            'order_line_set-0-item': self.item.pk,  # Correct prefix and field value
            'order_line_set-0-description': 'Test description',
            'order_line_set-0-quantity': 1,
            'order_line_set-0-price': 100,
            'order_line_set-TOTAL_FORMS': '1',
            'order_line_set-INITIAL_FORMS': '0',
        }

        # Payment form data
        payment_data = {
            'cash_received': Decimal(120),  # Example field from CashPaymentForm
            'amount': Decimal(120),  # Adjust based on form fields
        }
        
        # Merge all data for the POST request
        post_data = {**sale_data, **order_data, **payment_data}
        
        # Post request to the SaleCreateView
        response = self.client.post(reverse('sale:order-create'), post_data)

        # Add some print debugging for the forms
        sale_form = SaleForm(post_data)
        orders = OrderFormSet(post_data)
        payment_form = CashPaymentForm(post_data)
        
        print("Sale Form Valid:", sale_form.is_valid())
        print("Sale Form Errors:", sale_form.errors)
        print("Orders Valid:", orders.is_valid())
        print("Orders Errors:", orders.errors)
        print("Payment Form Valid:", payment_form.is_valid())
        print("Payment Form Errors:", payment_form.errors)

        # If the forms are valid, check the response for a redirect
        if sale_form.is_valid() and orders.is_valid() and payment_form.is_valid():
            # Expecting a redirect
            self.assertEqual(response.status_code, 302)
            sale = Sale.objects.latest('id')  # Get the latest sale created
            self.assertRedirects(response, reverse('sale:sale-detail', kwargs={'pk': sale.pk}))
        else:
            # Fail the test if forms are valid but the status code isn't 302
            self.fail("Forms are valid but redirect did not occur as expected.")
            
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('sale:sale-detail', kwargs={'pk': sale.pk}))
