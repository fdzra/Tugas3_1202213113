import graphene
import json
from flask import Flask
from flask_graphql import GraphQLView
import mysql.connector

app = Flask(__name__)

# Koneksi ke database MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="shoe_store"
)

mycursor = mydb.cursor()

class Shoe(graphene.ObjectType):
    id = graphene.ID()
    brand = graphene.String()
    model = graphene.String()
    size = graphene.Float()
    price = graphene.Float()

class Query(graphene.ObjectType):
    shoe = graphene.Field(Shoe)
    shoes = graphene.List(Shoe)
    shoe_by_id = graphene.Field(Shoe, id=graphene.ID())
    shoes_by_brand = graphene.List(Shoe, brand=graphene.String())

    def resolve_shoe(self, info):
        # Mendapatkan sepatu pertama dari database
        mycursor.execute("SELECT * FROM shoes LIMIT 1")
        result = mycursor.fetchone()
        return Shoe(id=result[0], brand=result[1], model=result[2], size=result[3], price=result[4])
  
    def resolve_shoes(self, info):
        # Mendapatkan semua sepatu dari database
        mycursor.execute("SELECT * FROM shoes")
        result = mycursor.fetchall()
        return [Shoe(id=row[0], brand=row[1], model=row[2], size=row[3], price=row[4]) for row in result]
    
    def resolve_shoe_by_id(self, info, id):
        # Mendapatkan sepatu berdasarkan ID dari database
        mycursor.execute("SELECT * FROM shoes WHERE id = %s", (id,))
        result = mycursor.fetchone()
        if result:
            return Shoe(id=result[0], brand=result[1], model=result[2], size=result[3], price=result[4])
        return None

    def resolve_shoes_by_brand(self, info, brand):
        # Mendapatkan sepatu berdasarkan merek dari database
        mycursor.execute("SELECT * FROM shoes WHERE brand = %s", (brand,))
        result = mycursor.fetchall()
        if result:
            return [Shoe(id=row[0], brand=row[1], model=row[2], size=row[3], price=row[4]) for row in result]
        return None

class ShoeInput(graphene.InputObjectType):
    brand = graphene.String()
    model = graphene.String()
    size = graphene.Float()
    price = graphene.Float()

class CreateShoe(graphene.Mutation):
    class Arguments:
        shoe = graphene.Argument(ShoeInput)

    shoe = graphene.Field(Shoe)

    def mutate(self, info, shoe):
        # Menyimpan sepatu baru ke database
        sql = "INSERT INTO shoes (brand, model, size, price) VALUES (%s, %s, %s, %s)"
        val = (shoe.brand, shoe.model, shoe.size, shoe.price)
        mycursor.execute(sql, val)
        mydb.commit()
        return CreateShoe(shoe=Shoe(brand=shoe.brand, model=shoe.model, size=shoe.size, price=shoe.price))

class UpdateShoe(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        shoe = graphene.Argument(ShoeInput)

    shoe = graphene.Field(Shoe)

    def mutate(self, info, id, shoe):
        # Mengupdate sepatu di database
        sql = "UPDATE shoes SET brand = %s, model = %s, size = %s, price = %s WHERE id = %s"
        val = (shoe.brand, shoe.model, shoe.size, shoe.price, id)
        mycursor.execute(sql, val)
        mydb.commit()
        return UpdateShoe(shoe=Shoe(id=id, brand=shoe.brand, model=shoe.model, size=shoe.size, price=shoe.price))

class DeleteShoe(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    shoe_id = graphene.ID()

    def mutate(self, info, id):
        # Menghapus sepatu dari database
        sql = "DELETE FROM shoes WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        mydb.commit()
        return DeleteShoe(shoe_id=id)

class Mutation(graphene.ObjectType):
    create_shoe = CreateShoe.Field()
    update_shoe = UpdateShoe.Field()
    delete_shoe = DeleteShoe.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

if __name__ == '__main__':
    app.run(debug=True)
