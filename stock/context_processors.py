from .models import StockAlert

def stock_alerts(request):
    alerts = []
    items = StockAlert.objects.all()
    for item in items:
        if item.item.get_current_qte < item.threshold:
            alerts.append(item)

    return {

        'stock_alerts': alerts  # Make stock_alerts available in templates
    }