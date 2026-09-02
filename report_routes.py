from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify
from app.extensions import db
from app.models import Product, Customer, Sale, Payment

report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@report_bp.route('/dashboard', methods=['GET'])
def get_dashboard_summary():
    today = date.today()
    
    total_products = Product.query.count()
    total_stock_items = db.session.query(db.func.sum(Product.quantity)).scalar() or 0
    total_customers = Customer.query.count()
    
    # Sales
    all_sales = Sale.query.all()
    total_sales_amount = sum(s.total_amount for s in all_sales)
    today_sales_amount = sum(s.total_amount for s in all_sales if s.sale_date and s.sale_date.date() == today)

    # Payments
    all_payments = Payment.query.all()
    total_money_received = sum(p.amount_paid for p in all_payments)
    today_payments_amount = sum(p.amount_paid for p in all_payments if p.payment_date and p.payment_date.date() == today)

    # Balance
    all_customers = Customer.query.all()
    total_pending_balance = sum(c.remaining_balance for c in all_customers)

    # Low Stock
    low_stock_products = Product.query.filter(Product.quantity <= Product.minimum_stock).all()

    # Recent Sales & Payments
    recent_sales = Sale.query.order_by(Sale.id.desc()).limit(5).all()
    recent_payments = Payment.query.order_by(Payment.id.desc()).limit(5).all()

    return jsonify({
        'total_products': total_products,
        'total_stock_items': int(total_stock_items),
        'total_customers': total_customers,
        'today_sales': today_sales_amount,
        'total_sales': total_sales_amount,
        'total_money_received': total_money_received,
        'today_money_received': today_payments_amount,
        'total_pending_balance': total_pending_balance,
        'low_stock_count': len(low_stock_products),
        'low_stock_products': [p.to_dict() for p in low_stock_products],
        'recent_sales': [s.to_dict() for s in recent_sales],
        'recent_payments': [p.to_dict() for p in recent_payments]
    })

@report_bp.route('/analytics', methods=['GET'])
def get_analytics():
    # Last 7 days sales
    today = date.today()
    days_data = []
    for i in range(6, -1, -1):
        target_day = today - timedelta(days=i)
        day_str = target_day.strftime('%d %b')
        day_sales = Sale.query.filter(db.func.date(Sale.sale_date) == target_day).all()
        day_payments = Payment.query.filter(db.func.date(Payment.payment_date) == target_day).all()
        days_data.append({
            'date': day_str,
            'sales': sum(s.total_amount for s in day_sales),
            'received': sum(p.amount_paid for p in day_payments)
        })

    # Payment Methods Breakdown
    payments = Payment.query.all()
    method_counts = {}
    for p in payments:
        method_counts[p.payment_method] = method_counts.get(p.payment_method, 0.0) + p.amount_paid

    return jsonify({
        'weekly_trend': days_data,
        'payment_methods': method_counts
    })
