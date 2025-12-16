import matplotlib.pyplot as plt
import pandas as pd
import json
import tempfile
import datetime
from django.db.models import Max
from stock.models import ReceiptItem,Stock
date_today = datetime.date.today()
import decimal
from math import sqrt
import os 
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import os
import base64

import asyncio
import logging # It's good practice to log errors

logger = logging.getLogger(__name__)










