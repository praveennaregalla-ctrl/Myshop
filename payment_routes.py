from datetime import datetime, date
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Payment, Customer, Sale

payment_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@payment_bp.route('', methods=['GET'])
def get_payments():
    customer_id = request.args.get('customer_id', type=int)
    date_str = request.args.get('date') # YYYY-MM-DD
    payment_method = request.args.get('method')

    query = Payment.query
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if payment_method and payment_method != 'All':
        query = query.filter_by(payment_method=payment_method)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Payment.payment_date) == target_date)
        except ValueError:
            pass

    payments = query.order_by(Payment.payment_date.desc(), Payment.id.desc()).all()
    total_received = sum(p.amount_paid for p in payments)
    
    return jsonify({
        'total_received': total_received,
        'count': len(payments),
        'payments': [p.to_dict() for p in payments]
    })

@payment_bp.route('/date/<string:date_str>', methods=['GET'])
def get_payments_by_date(date_str):
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        payments = Payment.query.filter(db.func.date(Payment.payment_date) == target_date).order_by(Payment.id.desc()).all()
        daily_total = sum(p.amount_paid for p in payments)
        return jsonify({
            'date': date_str,
            'daily_total': daily_total,
            'count': len(payments),
            'payments': [p.to_dict() for p in payments]
        })
    except ValueError:
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400

@payment_bp.route('', methods=['POST'])
def record_payment():
    data = request.get_json() or {}
    customer_id = data.get('customer_id')
    customer_name = data.get('customer_name', 'Customer')
    amount_paid = float(data.get('amount_paid', 0.0))
    payment_method = data.get('payment_method', 'Cash')
    item_description = data.get('item_description', 'Payment Collection')
    payment_notes = data.get('payment_notes', '')
    payment_date_str = data.get('payment_date')

    if amount_paid <= 0:
        return jsonify({'error': 'Payment amount must be greater than 0'}), 400

    payment_date = datetime.utcnow()
    if payment_date_str:
        try:
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d')
        except ValueError:
            pass

    try:
        customer = Customer.query.get(customer_id) if customer_id else None
        current_remaining = customer.remaining_balance if customer else 0.0
        new_remaining = max(0.0, current_remaining - amount_paid)

        payment = Payment(
            customer_id=customer_id,
            customer_name=customer.name if customer else customer_name,
            sale_id=data.get('sale_id'),
            item_description=item_description,
            total_amount=current_remaining,
            amount_paid=amount_paid,
            remaining_balance=new_remaining,
            payment_method=payment_method,
            payment_notes=payment_notes,
            payment_date=payment_date
        )
        db.session.add(payment)

        # Update Customer
        if customer:
            customer.total_amount_paid += amount_paid
            customer.remaining_balance = new_remaining

        db.session.commit()
        return jsonify(payment.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
