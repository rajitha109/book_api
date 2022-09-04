from email.policy import default
from hashlib import new
from flask import Flask, jsonify,request
from flask_restx import Api,Resource,fields
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime 


basedir=os.path.dirname(os.path.realpath(__file__))

#print(basedir)


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'books.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_ECHO']=True

api=Api(app,doc="/",title="A Book API",description="A simple REST API for BOOK")

db= SQLAlchemy(app)


class Book(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(25),nullable=False)
    author=db.Column(db.String(40),nullable=False)
    date_added=db.Column(db.DateTime(),default=datetime.utcnow())

    def __repr__(self):
        return self.title

book_model=api.model(
    'Book',
    {
        'id':fields.Integer(),
        'title':fields.String(),
        'author':fields.String(),
        'date_joined':fields.String()
    }
)      





@api.route('/books')
class Books(Resource):

    @api.marshal_list_with(book_model,code=200,envelope="books")   
    def get(self):
        '''Get all Books'''
        books=Book.query.all()
        return books,200

    @api.marshal_list_with(book_model,code=201,envelope="book")
    @api.doc(params={'title':'A title','author':'An Author'})
    def post(self):
        '''Create a new Book'''
        data=request.get_json()
        title=data.get('title')
        author=data.get('author')
        new_book = Book(title=title,author=author)

        db.session.add(new_book)
        db.session.commit()

        return new_book,201
          



@api.route('/books/<int:id>')
class BookResourse(Resource):
    @api.marshal_list_with(book_model,code=200,envelope="books")
    def get(self,id):
        '''Get one Book'''
        book=Book.query.get_or_404(id)
        return book,200


    @api.marshal_list_with(book_model,envelope="book",code=200)
    def put(self,id):
        '''Update a Book'''
        book_to_update=Book.query.get_or_404(id)
        data= request.get_json()
        book_to_update.title=data.get('title')
        book_to_update.author=data.get('author')
        db.session.commit()   

        return book_to_update,200    

    @api.marshal_list_with(book_model,envelope="books_deleted",code=200)
    def delete(self,id):
        '''Delete a Book'''
        book_to_delete=Book.query.get_or_404(id)
        db.session.delete(book_to_delete)
        db.session.commit()

        return book_to_delete,200


        

@app.shell_context_processor
def make_shell_context():
    return {
        "db":db,
        "Book":Book
    }


if __name__ == "__main__":
    app.run(debug=True)
