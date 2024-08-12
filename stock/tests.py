from django.test import TestCase
import unittest
from .models import Item
        
class TheTestCase(unittest.TestCase):
    def test_get_current_qte(self):
        lwad = Item.objects.get(id=8)
        current_qte = lwad.get_current_qte()
        self.assertEqual(current_qte,100)