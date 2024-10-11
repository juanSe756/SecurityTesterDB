from typing import List

from fastapi import FastAPI, HTTPException
import asyncpg  # Importar asyncpg para conexión a PostgreSQL
from pydantic import BaseModel

app = FastAPI()

# BaseModel para validar datos de entrada
class LoginRequest(BaseModel):
    email: str
    password: str

class OrderRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

# Modelo para la respuesta de la orden
class OrderResponse(BaseModel):
    user_id: int
    product_id: int
    quantity: int

# Conexión a la base de datos
async def connect_db():
    conn = await asyncpg.connect(
        user='postgres',         # Cambia por tu usuario
        password='admin',  # Cambia por tu contraseña
        database='DBtests', # Cambia por el nombre de tu base de datos
        host='localhost',          # Cambia si tu base de datos está en otra dirección
    )
    return conn
@app.post("/login/")
async def login(request: LoginRequest):
    conn = await connect_db()
    try:
        # Consulta SQL NO vulnerable
        query = "SELECT * FROM users WHERE email = $1 AND password = $2"
        user = await conn.fetchrow(query, request.email, request.password)

        if user:
            return {"message": "Successfully logged in"}
        raise HTTPException(status_code=401, detail="Wrong credentials")
    finally:
        await conn.close()

@app.post("/order/")
async def create_order(request: OrderRequest):
    conn = await connect_db()

    # Intentar insertar un pedido
    try:
        query = "INSERT INTO orders (user_id, product_id, quantity) VALUES ($1, $2, $3)"
        await conn.execute(query, request.user_id, request.product_id, request.quantity)

        return {"message": "Order created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create order: {str(e)}")
    finally:
        await conn.close()

@app.get("/orders/", response_model= List[OrderResponse])
async def get_orders():
    conn = await connect_db()
    try:
        # Consulta para obtener todas las órdenes
        query = "SELECT user_id, product_id, quantity FROM orders"
        rows = await conn.fetch(query)

        # Convertir los resultados en una lista de diccionarios
        orders = [{"user_id": row["user_id"], "product_id": row["product_id"], "quantity": row["quantity"]} for row in rows]

        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve orders: {str(e)}")
    finally:
        await conn.close()