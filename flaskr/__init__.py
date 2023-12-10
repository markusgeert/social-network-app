from flask import Flask, render_template, url_for

def create_app():
    app = Flask(__name__)

    @app.get('/')
    def home():
        users = [
            {
                'firstname': 'John',
                'lastname': 'Doe',
                'avatar_url': url_for('static', filename='profiles/john.png'),
                'age': 53,
                'favourite holiday': 'Beach',
                'favourite season': 'Autumn',
                'favourite food': 'Pasta' 
            },
            {
                'firstname': 'Mary',
                'lastname': 'Jane',
                'avatar_url': url_for('static', filename='profiles/mary.png'),
                'age': 56,
                'favourite holiday': 'Beach',
                'favourite season': 'Spring',
                'favourite food': 'Pizza' 
            }
        ]
        displayed_fields = ['age', 'favourite holiday', 'favourite season', 'favourite food']

        return render_template('index.html', users=users, fields=displayed_fields)

    @app.get('/admin')
    def admin():
        return render_template('admin.html')

    return app
