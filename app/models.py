from app import db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    client_code = db.Column(db.String(6), unique=True, nullable=False)
    contacts = db.relationship('Contact', secondary='client_contact', backref='clients')

    def generate_client_code(self):
        base_code = ''.join([char for char in self.name.upper() if char.isalpha()][:3])
        base_code = base_code.ljust(3, 'A')
        existing_codes = [code.client_code for code in Client.query.all()]
        num = 1
        while f"{base_code}{num:03}" in existing_codes:
            num += 1
        self.client_code = f"{base_code}{num:03}"


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


client_contact = db.Table('client_contact',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id'), primary_key=True)
)
