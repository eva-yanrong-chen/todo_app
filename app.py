from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gogumalatte@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__='todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo: {self.id} {self.description}>'

#   Since we're using Migrations, we won't need db.create_all() to sync our model anymore
#   db.create_all()

class TodoList(db.Model):
    __tablename__='todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)


@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        #   description = request.form.get('description', '') # the '' is a default empty string in case no text came in
        #   for AJAX request, we no longer uses html form to get our data
        description = request.get_json()['description'] #   We will use get_json to get the dictionary
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        #   After adding new todo item to the table, the app will redirect to '/' route
        #   return redirect(url_for('index'))
        #   Instead of redirecting, we will want to return a useful JSON object that includes the description
        return jsonify(body)


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

@app.route('/')
#   The index method is the controller
#   It tells the view to show index.html; it tells the model to do a SELECT * FROM todos
def index():
    #   Specifying a html file from your templates folder when user visits
    # this route using render template
    #   We can also pass in variable with the html file in render_template
    return render_template('index.html', data=Todo.query.order_by('id').all())

