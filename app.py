from flask import Flask, render_template, request, jsonify,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcton.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(10), nullable=False) 
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)


@app.route('/edit_payment/<int:id>', methods=['POST'])
def edit_payment(id):
    payment = Payment.query.get(id)
    if payment:
        return render_template('edit_form.html', payment=payment)
    

@app.route('/update_payment/<int:id>', methods=['POST'])
def update_payment(id):
    payment = Payment.query.get(id)
    if payment:
        
        if payment.amount is None or payment.category is None or payment.description is None or payment.date is None :
            return render_template("edit_form.html",message="Invalid data or empty data")
        
        try:
           payment.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        except ValueError:
                return render_template("edit_form.html", payment=payment,message="Invalid date format. Please use YYYY-MM-DD.")
        payment.amount = request.form.get('amount')
        payment.category = request.form.get('category')
        payment.description = request.form.get('description')
        payment.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')

        db.session.commit()

        return redirect(url_for('home'))  
   
    


@app.route('/delete_payment/<int:id>', methods=['POST'])
def delete_payment(id):
    payment = Payment.query.get(id)
    if payment:
        db.session.delete(payment)
        db.session.commit()
        payments = Payment.query.all()  
        return render_template('index.html', payments=payments)

@app.route("/filter_data", methods=["GET"])
def filter_data():
    category = request.args.get('category')
    if category in ['debit', 'credit']:
        payments = Payment.query.filter_by(category=category).all()
    else:
        payments = Payment.query.all()
    return render_template('index.html', payments=payments) 


@app.route('/form')
def fill_form():
    return render_template("form.html")

@app.route('/')
def home():
    payments = Payment.query.all()  
    return render_template('index.html', payments=payments)

@app.route('/api/submit', methods=['POST'])
def submit_payment():
    try:
        data = request.get_json()
        if not all(key in data for key in ('amount', 'category', 'description', 'date')):
            return render_template("form.html",message="Invalid data")

        amount = data.get('amount')
        category = data.get('category')
        description = data.get('description')
        date = data.get('date')

        if amount is None or category is None or description is None or date is None :
            return render_template("form.html",message="Invalid data or empty data")

        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return render_template("form.html",message="Invalid data or empty data")

       
        new_payment = Payment(
            amount=amount,
            category=category,
            description=description,
            date=date_obj  
        )

        db.session.add(new_payment)
        db.session.commit()
        return redirect(url_for('home'))


    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "An error occurred", "status": "error"})

@app.route('/api/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all() 
    payment_list = []

    for payment in payments:
        payment_list.append({
            'id': payment.id,
            'amount': payment.amount,
            'category': payment.category,
            'description': payment.description,
            'date': payment.date.strftime('%Y-%m-%d')  
        })

    return jsonify(payment_list) 


if __name__ == "__main__":
    app.run(debug=True)
