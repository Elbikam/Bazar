from django.test import TestCase,Client
from django.urls import reverse
from sale.models import *
from sale.forms import *
from stock.models import *
from decimal import Decimal
from django.urls import reverse_lazy
from django.shortcuts import redirect

# class SaleCreateViewTests(TestCase):
#     def setUp(self):
#         self.client = Client()

#         # Create a regular user
#         self.user = User.objects.create_user(username='regularuser', password='testpassword')

#         # Create a superuser (who should pass the test in UserPassesTestMixin)
#         self.superuser = User.objects.create_superuser(username='superuser', password='testpassword')
#         # Create necessary test data
#         i = Item.objects.create(
#             id=1,
#             name='Test Item',
#             category='Test Category',
#             description='Test description',
#             price=100
#         )
       
#         self.item = Stock.objects.create(item=i, current_quantity=100,unit_by_carton=5)
#     def test_access_denied_for_regular_user(self):
#         # Log in as a regular user
#         # self.client.login(username='regularuser', password='testpassword')

#         # Try to access the SaleCreateView
#         response = self.client.get(reverse('sale:order-create'))  

#         # Check if the user is redirected to the login page or "no permission" page
#         self.assertEqual(response.status_code,302)
        
#         # self.assertRedirects(response, reverse('dashboard:login'))  

#     def test_access_granted_for_superuser(self):
#         # Log in as a superuser
#         self.client.login(username='superuser', password='testpassword')

#         # Try to access the SaleCreateView
#         response = self.client.get(reverse('sale:order-create'))

#         # Check if the superuser can access the view (expect a 200 OK response)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'sale/order_form.html')  
    # def test_get_request(self):
    #     sale_from = SaleForm()
    #     orders = OrderFormSet()
    #     context = {
    #         'sale_form':sale_from,
    #         'orders':orders,
    #     }
    #     response=self.client.get(reverse('sale:order-create'),context)
    #     # self.assertEqual(response.status_code,200) 

    # def test_post_request_successful_sale_creation(self):
    #     sale_data = {
    #         'date': '2024-10-27 12:12:29.889337',  
    #     }
    
    #     order_data = {
    #         'order_line_set-0-item':self.item.pk,  
    #         'order_line_set-0-description': 'Test description',
    #         'order_line_set-0-quantity': 1, 
    #         'order_line_set-0-price': 100,
    #         'order_line_set-TOTAL_FORMS': '1',
    #         'order_line_set-INITIAL_FORMS': '0',
    #     }

    #     # Payment form data
    #     payment_data = {
    #         'cash_received': Decimal(120),  # Example field from CashPaymentForm
    #         'amount': Decimal(120),  # Adjust based on form fields
    #     }
        
    #     # Merge all data for the POST request
    #     post_data = {**sale_data, **order_data, **payment_data}
        
    #     # Post request to the SaleCreateView
    #     response = self.client.post(reverse('sale:order-create'), post_data)

    #     # Add some print debugging for the forms
    #     sale_form = SaleForm(post_data)
    #     orders = OrderFormSet(post_data)
    #     payment_form = CashPaymentForm(post_data)
        
    #     print("Sale Form Valid:", sale_form.is_valid())
    #     print("Orders Valid:", orders.get_default_prefix())
    #     print("Payment Form Valid:", payment_form.is_valid())
  
    #     sale = Sale.objects.latest('id')
    #     # self.assertContains(response,'Insufficient stock for Test Item: 100 Units in Stock') 
    #     self.assertEqual(sale.get_HT, Decimal(100))
        
    #     self.assertEqual(response.status_code,302)
    #     self.assertRedirects(response, reverse('sale:sale-detail', kwargs={'pk': sale.pk}))


# class DevisCreateViewTest(TestCase):
#     def setUp(self):
#         # Create necessary test data
#         i = Item.objects.create(
#             id=111,
#             name='Test Item',
#             category='Test Category',
#             description='Test description',
#             price=100
#         )
#         self.item = Stock.objects.create(item=i, current_quantity=20,unit_by_carton=5)
#         # self.item = Stock.objects.create(item=i, get_current_qte=10)

#     def test_get_request(self):
#         devis_from = DevisForm()
#         orders = DOrderFormSet()
#         context = {
#             'devis_form':devis_from,
#             'orders':orders,
#         }
#         response=self.client.get(reverse('sale:devis-create'),context)
#         self.assertEqual(response.status_code,200) 
#     def test_post_request(self):
#         devis_data = {
#             'customer':'Boubaker Elbikam',
#         }
#         order_data = {
#             'devis_line_set-0-item': self.item.pk,  # Correct prefix and field value
#             'devis_line_set-0-description': 'Test description',
#             'devis_line_set-0-quantity': 1,
#             'devis_line_set-0-price': 100,
#             'devis_line_set-TOTAL_FORMS': '1',
#             'devis_line_set-INITIAL_FORMS': '0',
#         }
#         post_data = {**devis_data, **order_data}
#         respponse = self.client.post(reverse('sale:devis-create'),post_data)
#         devis = Devis.objects.latest('id')
#         self.assertEqual(respponse.status_code,302)
#         self.assertRedirects(respponse,reverse('sale:devis-detail',kwargs={'pk':devis.pk}))

# class DealerCreateTest(TestCase):
#     def setUp(self):
#         return super().setUp()
#     def test_get(self):
#         dealer_form = DealerForm()
#         context = {
#             'dealer_form':dealer_form,
#         }
#         response = self.client.get(reverse('sale:dealer-create'),context)
#         self.assertTemplateUsed(response,'sale/dealer_form.html')
#         self.assertEqual(response.status_code,200)
#     def test_post(self):
#         dealer_data = {
#             'name':'boubaker elbikam',
#             'phone_whatsapp':+212123456789,
#             'balance_limit':1000,


#         }  
#         post_data = {**dealer_data}
#         response = self.client.post(reverse('sale:dealer-create'),post_data)
#         self.assertEqual(response.status_code,302)
# class SaleToDealerCreateView(TestCase):
#     def setUp(self):
#         d = Dealer.objects.create(created_at='2024-10-28',name='Bob',
#             phone_whatsapp = '+212123456789',is_active=True,balance=0,
#             balance_limit=1000)
#         i = Item.objects.create(
#             id=1,
#             name='Test Item',
#             category='Test Category',
#             description='Test description',
#             price=100
#         )
#         self.j = Item.objects.create(
#             id=2,
#             name='Test Item',
#             category='Test Category',
#             description='Test description',
#             price=100
#         )
#         self.dealer = d
#         self.item = Stock.objects.create(item=i, current_quantity=100,unit_by_carton=5)
#     def test_get(self):
#         sale_to_dealer_from = SaleToDealerForm()
#         orders = OrderFormSet()
#         context = {
#             'sale_to_dealer':sale_to_dealer_from,
#             'orders':orders,

#         }
#         response = self.client.get(reverse('sale:dealer-sale'),context)
#         self.assertEqual(response.status_code,200)
#         self.assertTemplateUsed(response,'sale/dealer_sale_form.html')
    
#     def test_post(self):
#         sale_data = {
#             'date':'2024-10-27 10:36:29.889337',
#             'dealer':self.dealer.pk,
#         }
#         order_data = {
#             'order_line_set-0-item':self.item.pk,  
#             'order_line_set-0-description': 'Test description',
#             'order_line_set-0-quantity': 20, 
#             'order_line_set-0-price': 100,
#             'order_line_set-TOTAL_FORMS': '1',
#             'order_line_set-INITIAL_FORMS': '0',
#         }
#         post_data = {**sale_data,**order_data}
#         response = self.client.post(reverse('sale:dealer-sale'),post_data)
#         sale_form = SaleToDealerForm(post_data)
#         order_form = OrderFormSet(post_data)
        
#         # sale = SaleToDealer.objects.latest('id')
        
#         self.assertEqual(response.status_code,302)
#         self.assertRedirects(response,reverse('sale:balance-limit-error'))
#         # self.assertContains(response,'Insufficient stock for Test Item: 1 Units in Stock')

# class MonthlyPyamentTest(TestCase):
#     def setUp(self):
#         d = Dealer.objects.create(created_at='2024-10-28',name='Bob',
#             phone_whatsapp = '+212123456789',is_active=True,balance=900,
#             balance_limit=1000)
#         self.dealer = d
#     def test_get(self):
#         form = MonthlyPaymentForm()
#         context = {
#             'form':form
#         }
#         response = self.client.get(reverse('sale:monthly-payment-create'),context)
#         self.assertEqual(response.status_code,200)
       
#     def test_post(self):
#         payment_data = {
#             'dealer':self.dealer.pk,
#             'amount':400,


#         }
#         post_data = {**payment_data}
#         response = self.client.post(reverse('sale:monthly-payment-create'),post_data)
#         monthly_payment = MonthlyPayment.objects.latest('id')
#         self.assertRedirects(response,reverse('sale:monthly-payment',kwargs={'pk':monthly_payment.pk}))

# class RefundCreateViewTest(TestCase):
#     def setUp(self):
#         #  Create necessary test data
#         i = Item.objects.create(
#             id=1,
#             name='Test Item',
#             category='Test Category',
#             description='Test description',
#             price=100
#         )
       
#         self.item = Stock.objects.create(item=i, current_quantity=100,unit_by_carton=5)
#         s=Sale.objects.create(date='2024-10-28 16:45:58.062980')
#         self.sale = s
#     def test_get(self):
#         refund_from = RefundForm()
#         orders = RefundFormSet()
#         context = {
#             'refund_form':refund_from,
#             'orders': orders,
           
#         }
#         response = self.client.get(reverse('sale:refund-create'),context)
#         # self.assertEqual(response.status_code,200)
#         # self.assertTemplateUsed(response,'sale/refund_form.html'  )
#     def test_post(self):
#         refund_data = {
#             'so':self.sale.pk ,
#             'reason':'ERROR',

#         }
#         order_data = {
#             'refund_line_set-0-item':self.item.pk,  
#             'refund_line_set-0-description': 'Test description',
#             'refund_line_set-0-quantity': 2, 
#             'refund_line_set-0-price': 100,
#             'refund_line_set-TOTAL_FORMS': '1',
#             'refund_line_set-INITIAL_FORMS': '0',
#         }
#         post_data = {**refund_data,**order_data}
#         response = self.client.post(reverse('sale:refund-create'),post_data)
#         # self.assertEqual(response.status_code,302)
#         refund_form = RefundForm(post_data)
#         order_form = RefundFormSet(post_data)
#         print('refund is :',refund_form.is_valid())
#         print('refund is :',refund_form.errors)
#         print('order_form is :',order_form.is_valid())
#         self.assertEqual(response.status_code,302)
       
# class RefundDealerCreateViewTest(TestCase):
#     def setUp(self):
#         #  Create necessary test data
#         d = Dealer.objects.create(created_at='2024-10-28',name='Bob',
#             phone_whatsapp = '+212123456789',is_active=True,balance=0,
#             balance_limit=1000)
#         i = Item.objects.create(
#             id=1,
#             name='Test Item',
#             category='Test Category',
#             description='Test description',
#             price=100
#         )
       
#         self.item = Stock.objects.create(item=i, current_quantity=100,unit_by_carton=5)
#         s=SaleToDealer.objects.create(date='2024-10-28 16:45:58.062980',dealer=d)
#         self.sale = s
        
#     def test_get(self):
#         refund_form = RefundFromDealerForm()
#         refunds = RefundFormSet()
#         context = {
#             'refund_form': refund_form,
#             'refunds': refunds,
           
#         }
#         response = self.client.get(reverse('sale:refund-dealer-create'),context)
#         self.assertTemplateUsed(response,'sale/refund_dealer_form.html')

#     def test_post(self):
#         refund_data = {
#             'so':self.sale.pk ,
#             'dealer':self.sale.dealer.pk,
#             'reason':'ERROR',

#         }
#         order_data = {
#             'refund_line_set-0-item':self.item.pk,  
#             'refund_line_set-0-description': 'Test description',
#             'refund_line_set-0-quantity': 1, 
#             'refund_line_set-0-price': 100,
#             'refund_line_set-TOTAL_FORMS': '1',
#             'refund_line_set-INITIAL_FORMS': '0',
#         }
#         post_data = {**refund_data,**order_data}
#         response = self.client.post(reverse('sale:refund-dealer-create'),post_data)
#         refund_form = RefundFromDealerForm(post_data)
#         order_form = RefundFormSet(post_data)
#         print('refunf_form is:',refund_form.is_valid())
#         print('order is valid:',order_form.is_valid())
#         refund = RefundFromDealer.objects.latest('id')
#         self.assertEqual(response.status_code,302)

#         self.assertRedirects(response,reverse('sale:refund-dealer-payment',kwargs={'pk':refund.pk}))

