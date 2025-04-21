from flask import Flask, request, jsonify
from models import db, Todo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# ✅ アプリの起動時に初期化（初回のみ）
def init_db_and_seed():
    with app.app_context():
        db.create_all()

        # 初期データがなければ挿入
        if not Todo.query.first():
            sample_todos = [
                Todo(title="買い物に行く", done=False),
                Todo(title="読書をする", done=False),
                Todo(title="コードを書く", done=True)
            ]
            db.session.bulk_save_objects(sample_todos)
            db.session.commit()
            print("✅ 初期データを挿入しました")


# 初期化処理を明示的に呼ぶ
init_db_and_seed()


@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos])


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())


@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    todo = Todo(title=data['title'], done=False)
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    todo.title = data.get('title', todo.title)
    todo.done = data.get('done', todo.done)
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    app.run()
