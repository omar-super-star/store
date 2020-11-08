from flask import *
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
database_filename = "database.sqlite"
project_dir = os.path.dirname(os.path.abspath(__file__))
print(project_dir)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, database_filename))
app.config['UPLOAD_FOLDER'] =project_dir+"/static/image"
app.secret_key = "bhbnbjblkbkbkbkjb454213356165"
db = SQLAlchemy(app)

class product(db.Model):
    id = db.Column(db.Integer().with_variant(db.Integer, "sqlite"), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    descreption =  db.Column(db.String(180), nullable=True)
    image_url =  db.Column(db.String(250), nullable=True)
   

class order(db.Model):
    id = db.Column(db.Integer().with_variant(db.Integer, "sqlite"), primary_key=True)
    name=db.Column(db.String(80), unique=True)
    address=db.Column(db.String(180), nullable=True)
    number=db.Column(db.Integer(), nullable=True)
    product=db.Column(db.Integer(),db.ForeignKey('product.id'),
        nullable=False)
    finish=db.Column(db.Integer(),default=0)
class finish_order(db.Model):
    id = db.Column(db.Integer().with_variant(db.Integer, "sqlite"), primary_key=True)
    order=product=db.Column(db.Integer(),db.ForeignKey('order.id'),
        nullable=False)


@app.route("/add_product",methods=["GET"])
def add_product_form():
    try:
        return render_template("form_add.html",
        url=session["url_form"]
                               )
    except:
        return render_template("form_add.html",
                               url=""
                               )

@app.route("/")
def get_the_url():
    session["url_form"]=request.base_url+session["url_form"]
    return redirect(url_for("add_product_form"))
@app.route("/add_product",methods=["POST"])
def new_order():
    global form_url
    file=request.files.get("image")
    filename=secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    p=product(name=request.form.get("name"),
              descreption=request.form.get(" description"),
              image_url=filename)
    db.session.add(p)
    db.session.commit()
    
    session["url_form"]="add_order/"+str(p.id)
    return redirect(url_for("get_the_url"))

@app.route("/add_order/<id>",methods=["POST"])
def order_post(id):
    o=order(name=request.form.get("name"),
              address=request.form.get("address"),
              number=request.form.get("number"),
              product=id)
    db.session.add(o)
    db.session.commit()
    return redirect(url_for("order_get",id=id))
@app.route("/add_order/<id>",methods=["GET"])
def order_get(id):
   return render_template("form_order.html",id=id)

@app.route("/finish_order/<id>",methods=["POST"])
def finish_order_fun(id):
    o=db.session.query(order).filter_by(id=id).one()
    o.finish=1
    db.session.commit()
    finish_ord=finish_order(order=id)
    db.session.add(finish_ord)
    db.session.commit()
    return redirect(url_for("order_show"))
@app.route("/user/show_finish_order",methods=["GET"])
def order_finish_show():
    orders=list(db.session.query(order).all())
    show=[]
    for o in orders:
        if o.finish == 0:
            continue
        show.append({"name":o.name,
                     "id":o.id,                  
                     "address":o.address,
                     "url":db.session.query(product).filter_by(id=o.product).one().image_url,
                     "number":o.number})
    print(orders)
    print(show)
    return render_template("orders.html",orders=show,finish=True)
@app.route("/user/show_order",methods=["GET"])
def order_show():
    orders=list(db.session.query(order).all())
    show=[]
    for o in orders:
        if o.finish == 1:
            continue
        show.append({"name":o.name,
        "id":o.id,
        "address":o.address,
        "url":db.session.query(product).filter_by(id=o.product).one().image_url,
        "number":o.number})
    print(orders)
    print(show)
    return render_template("orders.html",orders=show)

