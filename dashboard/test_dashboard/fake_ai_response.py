fake_ai_response = """
### 📊 Weekly Sales Analysis

I have analyzed the transaction data for the past week. Here are the key findings:

1.  **Top Performance**: The category **Electronics** is leading the charts with a total revenue of **$12,500**.
2.  **Low Performance**: *Home Goods* is underperforming compared to last month.
3.  **Action Items**:
    - Restock iPhone 15 units.
    - Launch a discount campaign for bedsheets.

Below is the visualization of the sales distribution:

<artifact>
<div style="position: relative; height:300px; width:100%">
    <canvas id="salesChart"></canvas>
</div>
<script>
    (function() {
        const ctx = document.getElementById('salesChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Electronics', 'Clothing', 'Home Goods', 'Sports'],
                    datasets: [{
                        label: 'Revenue ($)',
                        data: [12500, 8400, 3200, 5600],
                        backgroundColor: [
                            '#4CAF50', // Green
                            '#2196F3', // Blue
                            '#FFC107', // Amber
                            '#9C27B0'  // Purple
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }
    })();
</script>
</artifact>

**Conclusion**: Overall, revenue is up by **15%** compared to the previous period.
"""