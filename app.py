from app import create_app

# create flask application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
