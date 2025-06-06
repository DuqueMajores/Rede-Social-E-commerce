#import secrets
#print(secrets.token_hex(24))

from app import app

"""db"""
"""from app.models import Notificacao

with app.app_context():
    db.session.query(Notificacao).delete()
    db.session.commit()"""

if __name__ == '__main__':
     app.run(debug=True, port=3000)
