from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Client, Contact

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('base.html')

@main.route('/clients', methods=['GET', 'POST'])
def clients():
    if request.method == 'POST':
        name = request.form['name']
        if name:
            client = Client(name=name)
            client.generate_client_code()
            db.session.add(client)
            db.session.commit()
            flash('Client added successfully!', 'success')
        else:
            flash('Client name is required!', 'danger')
    clients = Client.query.order_by(Client.name).all()
    return render_template('clients.html', clients=clients)

@main.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        if name and surname and email:
            contact = Contact(name=name, surname=surname, email=email)
            db.session.add(contact)
            db.session.commit()
            flash('Contact added successfully!', 'success')
        else:
            flash('All fields are required!', 'danger')
    contacts = Contact.query.order_by(Contact.surname, Contact.name).all()
    return render_template('contacts.html', contacts=contacts)
