from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/register')
    def register():
        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/new_ticket')
    def new_ticket():
        return render_template('new_ticket.html')

    @app.route('/tickets')
    def tickets():
        return render_template('tickets.html')



    return app
