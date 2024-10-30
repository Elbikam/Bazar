from django.test import TestCase
import unittest
from .models import *
from .forms import *

from django.urls import reverse
        
# class StockTestCase(TestCase):
#     def setUp(self):
#         item =Item.objects.create(id=123,name='laspalams',category='THE VERT', description='lasplams 4011',price=100)
#         s = Stock.objects.create(item=item,current_quantity=10,unit_by_carton=5)

#     def test_get_current_qte(self):
#         laspalmas = Stock.objects.get(id=1)
#         self.assertEqual(laspalmas.get_current_qte,10)
#         self.assertEqual(laspalmas.qte_by_carton,5)
#         self.assertEqual(laspalmas.quantity_by_crtn,'2 cartons | 0 Unit')

# class ReceiptTestCase(TestCase):
#     def setUp(self):
#         r = Receipt.objects.create(date='2024-10-29',bon_de_livraison=1,qte_total=100,qte_by_carton=20)
#         i =Item.objects.create(id=123,name='laspalams',category='THE VERT', description='lasplams 4011',price=100)
#         j =Item.objects.create(id=13,name='laspalams',category='THE VERT', description='sss 4011',price=100)

#         ri=ReceiptItem.objects.create(receipt=r,item=i,description='laspalma 4011',quantity=50,unit_by_carton=5)
#         rj=ReceiptItem.objects.create(receipt=r,item=j,description='sss 4011',quantity=50,unit_by_carton=5)
#     def test_get_qte_total(self):
#         receipt = Receipt.objects.get(id=1)
#         self.assertEqual(receipt.get_qte_carton,receipt.qte_by_carton)

# class ItemCreateViewTest(TestCase):
#     def setUp(self):
#         # Set up any initial data if necessary. You can also create users here if authentication is required.
#         pass

#     def test_view_url_exists_at_desired_location(self):
#         response = self.client.get('/stock/item/create/')
#         self.assertEqual(response.status_code, 200)

#     def test_view_url_accessible_by_name(self):
#         response = self.client.get(reverse('stock:create_item'))
#         self.assertEqual(response.status_code, 200)

#     def test_view_uses_correct_template(self):
#         response = self.client.get(reverse('stock:create_item'))
#         self.assertTemplateUsed(response, 'stock/item_form.html')

#     def test_view_uses_item_form(self):
#         response = self.client.get(reverse('stock:create_item'))
#         self.assertIsInstance(response.context['form'], ItemForm)

#     def test_form_submission_successful(self):
#         data = {
#             'id':1,
#             'name': 'Test Item', 
#             'category':'THE VERT', # Replace with actual field names and data for Item
#             'description': 'This is a test item description',
#             'price':82,
#             # Add other fields here
#         }
#         response = self.client.post(reverse('stock:create_item'), data)
#         self.assertEqual(response.status_code, 302)  # Redirect after successful submission
#         self.assertRedirects(response, reverse('stock:item_list'))
#         self.assertEqual(Item.objects.count(), 1)  # Verify that an Item instance was created
#         self.assertEqual(Item.objects.first().name, 'Test Item')  # Check specific fields if needed

#     def test_form_submission_invalid(self):
#         data = {
#             'id':1,
#             'name': 'dd', # Empty name to trigger a form validation error
#             'category':'THE VERT',
#             'description': 'This is a test item description',
#             'price':'s',

#         }
#         # form = ItemForm(data)
#         # print('form is valid:',form.is_valid())
#         response = self.client.post(reverse('stock:create_item'), data)
#         response.render()
        
#         form = response.context['form']
#         self.assertIn('price', form.errors)  # Check that there’s an error on the 'price' field
#         self.assertEqual(form.errors['price'], ['Enter a number.']) 
            
class ReceiptCreateViewTest(TestCase):

    def setUp(self):
        self.i =Item.objects.create(id=123,name='laspalams',category='THE VERT', description='lasplams 4011',price=100)
        self.s = Stock.objects.create(item=self.i,current_quantity=10,unit_by_carton=5)

      
    def test_get(self):
        receipt_form = ReceiptForm()
        items = ReceiptItemFormSet()
        context = {
            'receipt_form':receipt_form,
            'items':items,
        }
        response = self.client.get(reverse('stock:create_receipt'),context)
        self.assertEqual(response.status_code,200)
    def test_post(self):
        
        receipt_data = {
            # 'date':'2024-10-29',
            'bon_de_livraison':1,
            'qte_total':100,
            'qte_by_carton':20,

        }
        receiptitem_data = {
       
            'items-item_id':self.i.pk, 
            'items-description':'Test description',
            'items-quantity': 10, 
            'items-unit_by_carton':5,
            'items-TOTAL_FORMS': 1,
            'items-INITIAL_FORMS': '0',
        }
        post_data = {**receipt_data,**receiptitem_data}
        response = self.client.post(reverse('stock:create_receipt'),post_data)
        receip_form = ReceiptForm(post_data)
        items= ReceiptItemFormSet(post_data)
        print('receipt is valid :',receip_form.is_valid())
        print('receipt item form :',items.is_valid())    
        self.assertEqual(response.status_code,302)


    
    
    