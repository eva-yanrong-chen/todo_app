from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gogumalatte@localhost:5432/todoapp'
db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__='todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Todo: {self.id} {self.description}>'

db.create_all()


@app.route('/todos/create', methods=['POST'])
def create_todo():
    description = request.form.get('description', '') # the '' is a default empty string in case no text came in
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    #   After adding new todo item to the table, the app will redirect to '/' route
    return redirect(url_for('index'))


@app.route('/')
#   The index method is the controller
#   It tells the view to show index.html; it tells the model to do a SELECT * FROM todos
def index():
    #   Specifying a html file from your templates folder when user visits
    # this route using render template
    #   We can also pass in variable with the html file in render_template
    return render_template('index.html', data=Todo.query.all())

