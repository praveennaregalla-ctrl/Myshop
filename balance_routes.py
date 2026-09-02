from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Customer, Sale, Payment, SaleItem

balance_bp = Blueprint('balances', __name__, url_prefix='/api/balances')

@balance_bp.route('', methods=['GET'])
def get_balance_book():
    status_filter = request.args.get('status') # pending, paid, all
    search = request.args.get('search')

    customers = Customer.query.order_by(Customer.remaining_balance.desc()).all()
    result = []
    
    for c in customers:
        if status_filter == 'pending' and c.remaining_balance <= 0:
            continue
        if status_filter == 'paid' and c.remaining_balance > 0:
            continue
        if search:
            if search.lower() not in c.name.lower() and search not in c.phone:
                continue

        # Find purchased items
        sales = Sale.query.filter_by(customer_id=c.id).order_by(Sale.id.desc()).all()
        items_summary = []
        for s in sales:
            for item in s.items:
                items_summary.append({
                    'sale_id': s.id,
                    'invoice_number': s.invoice_number,
                    'product_name': item.product_name,
                    'size': item.size,
                    'color': item.color,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price,
                    'date': s.sale_date.isoformat() if s.sale_date else None
                })

        status = 'Fully Paid' if c.remaining_balance <= 0 else ('Partially Paid' if c.total_amount_paid > 0 else 'Pending')
        result.append({
            'customer_id': c.id,
            'customer_name': c.name,
            'customer_phone': c.phone,
            'total_purchase_amount': c.total_purchase_amount,
            'total_amount_paid': c.total_amount_paid,
            'remaining_balance': c.remaining_balance,
            'status': status,
            'purchased_items': items_summary
        })

    total_pending = sum(c.remaining_balance for c in customers)
    return jsonify({
        'total_pending_balance': total_pending,
        'pending_customers_count': sum(1 for c in customers if c.remaining_balance > 0),
        'records': result
    })

@balance_bp.route('/add-due', methods=['POST'])
def add_customer_due():
    data = request.get_json() or {}
    customer_id = data.get('customer_id')
    amount = float(data.get('amount', 0.0))
    item_description = data.get('item_description', 'Credit Purchase')
    quantity = int(data.get('quantity', 1))
    unit_price = float(data.get('unit_price', amount / max(1, quantity)))
    notes = data.get('notes', '')

    if not customer_id or amount <= 0:
        return jsonify({'error': 'Customer ID and valid amount required'}), 400

    customer = Customer.query.get_or_404(customer_id)
    
    sale = Sale(
        invoice_number=f"CRD-{customer.id}-{int(datetime.utcnow().timestamp()) % 100000}",
        customer_id=customer.id,
        customer_name=customer.name,
        customer_phone=customer.phone,
        subtotal=amount,
        discount=0.0,
        total_amount=amount,
        amount_paid=0.0,
        remaining_balance=amount,
        payment_method='Credit Due',
        notes=notes
    )
    db.session.add(sale)
    db.session.flush()

    sale_item = SaleItem(
        sale_id=sale.id,
        product_name=item_description,
        size='-',
        color='-',
        quantity=quantity,
        unit_price=unit_price,
        total_price=amount
    )
    db.session.add(sale_item)

    customer.total_purchase_amount += amount
    customer.remaining_balance += amount

    db.session.commit()
    return jsonify({'message': 'Credit due added successfully', 'sale': sale.to_dict(), 'customer': customer.to_dict()})
