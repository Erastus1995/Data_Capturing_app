from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_capture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# Models
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    client_code = db.Column(db.String(6), unique=True, nullable=False)
    contacts = db.relationship('Contact', secondary='client_contact', back_populates='clients')

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    clients = db.relationship('Client', secondary='client_contact', back_populates='contacts')

class ClientContact(db.Model):
    __tablename__ = 'client_contact'
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), primary_key=True)

# Helper function to generate unique client codes
def generate_client_code(name):
    alpha_part = ''.join([c.upper() for c in name[:3] if c.isalpha()]).ljust(3, 'A')
    numeric_part = 1
    while True:
        code = f"{alpha_part}{numeric_part:03d}"
        if not Client.query.filter_by(client_code=code).first():
            return code
        numeric_part += 1

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Clients
@app.route('/clients', methods=['GET', 'POST'])
def manage_clients():
    if request.method == 'POST':
        name = request.form['name']
        if not name:
            flash('Name is required.', 'error')
            return redirect(url_for('manage_clients'))
        client_code = generate_client_code(name)
        new_client = Client(name=name, client_code=client_code)
        db.session.add(new_client)
        db.session.commit()
        flash('Client added successfully.', 'success')
    clients = Client.query.order_by(Client.name.asc()).all()
    return render_template('clients.html', clients=clients)

@app.route('/clients/<int:client_id>/link_contact', methods=['POST'])
def link_contact_to_client(client_id):
    contact_id = request.form['contact_id']
    client = Client.query.get_or_404(client_id)
    contact = Contact.query.get_or_404(contact_id)
    if contact not in client.contacts:
        client.contacts.append(contact)
        db.session.commit()
        flash('Contact linked successfully.', 'success')
    return redirect(url_for('view_client', client_id=client_id))

@app.route('/clients/<int:client_id>')
def view_client(client_id):
    client = Client.query.get_or_404(client_id)
    contacts = Contact.query.order_by(Contact.surname.asc()).all()
    return render_template('view_client.html', client=client, contacts=contacts)

# Contacts
@app.route('/contacts', methods=['GET', 'POST'])
def manage_contacts():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        if not all([name, surname, email]):
            flash('All fields are required.', 'error')
            return redirect(url_for('manage_contacts'))
        if Contact.query.filter_by(email=email).first():
            flash('Email must be unique.', 'error')
            return redirect(url_for('manage_contacts'))
        new_contact = Contact(name=name, surname=surname, email=email)
        db.session.add(new_contact)
        db.session.commit()
        flash('Contact added successfully.', 'success')
    contacts = Contact.query.order_by(Contact.surname.asc()).all()
    return render_template('contacts.html', contacts=contacts)

@app.route('/contacts/<int:contact_id>/link_client', methods=['POST'])
def link_client_to_contact(contact_id):
    client_id = request.form['client_id']
    contact = Contact.query.get_or_404(contact_id)
    client = Client.query.get_or_404(client_id)
    if client not in contact.clients:
        contact.clients.append(client)
        db.session.commit()
        flash('Client linked successfully.', 'success')
    return redirect(url_for('view_contact', contact_id=contact_id))

@app.route('/contacts/<int:contact_id>')
def view_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    clients = Client.query.order_by(Client.name.asc()).all()
    return render_template('view_contact.html', contact=contact, clients=clients)

# Database initialization
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
