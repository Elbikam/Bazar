from django.test import TestCase
import unittest
from .models import Sale
import decimal
# Create your tests here.
class SaleTestCase(unittest.TestCase):
    def setUp(self):
        Sale.objects.create()
    def test_get_HT(self):
        pass
        
    def test_total_of_items(self):
        pass
        
        
