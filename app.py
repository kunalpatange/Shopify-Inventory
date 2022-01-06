from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import io, csv
from werkzeug.utils import redirect

app= Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db= SQLAlchemy(app)


class Inventory(db.Model):
    id=db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.String(200), nullable=False)
    warehouse = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == "POST":
        task_code = request.form['code']
        new_task = Inventory(code=task_code, type=request.form['type'], title=request.form['title'], summary=request.form['summary'],
        warehouse=request.form['warehouse'], quantity= int(request.form['quantity']))
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "there was an issue"
    else:
        tasks = Inventory.query.order_by(Inventory.date_created).all()
        return render_template("index.html", tasks=tasks)


@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Inventory.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Problem while deleting the record"



@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    task = Inventory.query.get_or_404(id)
    if request.method == "POST":
        task.code = request.form['code']
        task.type = request.form['type']
        task.title = request.form['title']
        task.summary = request.form['summary']
        task.warehouse = request.form['warehouse']
        task.date_created = datetime.utcnow()
        task.quantity =  int(request.form['quantity'])
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Unable to update"
    else:
        return render_template('update.html',task=task)
    # task_to_update = Inventory.query.get_or_404(id)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        return "goo job"
    else:
        return render_template('add.html')


@app.route('/download')
def export():
     tasks = Inventory.query.order_by(Inventory.date_created).all()

     output = io.StringIO()
     writer = csv.writer(output)
     header =['Product Type','Product Name','Summary of Product','Quantity Available','Warehouse','Product Code','Date Created']
     writer.writerow(header)
     for row in tasks:
         line = row.type +','+row.title+','+row.summary+','+ str(row.quantity)+','+row.warehouse+','+row.code+','+ str(row.date_created) 
         line=line.split(',')
         writer.writerow(line)
     print(output.getvalue())
     res = make_response(output.getvalue())
     res.headers["Content-Disposition"] = "attachment; filename=shopify_inventory.csv"
     res.headers["Content-type"] = "text/csv"
     return res 
     
if __name__ == "__main__":
    app.run(debug=True)