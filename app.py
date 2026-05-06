import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# URL de conexión a PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')


# Función para obtener conexión a la base de datos
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# Función para crear las tablas si no existen
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            watering_frequency VARCHAR(100) NOT NULL,
            plant_type VARCHAR(100) NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# Crear tablas al iniciar la aplicación
create_tables()


# Ruta principal - Mostrar todas las plantas
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM plants ORDER BY id;')
    plants = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('index.html', plants=plants)


# Ruta para agregar una planta
@app.route('/add', methods=('GET', 'POST'))
def add_plant():

    if request.method == 'POST':
        name = request.form['name']
        watering_frequency = request.form['watering_frequency']
        plant_type = request.form['plant_type']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            '''
            INSERT INTO plants (name, watering_frequency, plant_type)
            VALUES (%s, %s, %s)
            ''',
            (name, watering_frequency, plant_type)
        )

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_plant.html')


# Ruta para editar una planta
@app.route('/edit/<int:plant_id>', methods=('GET', 'POST'))
def edit_plant(plant_id):

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        watering_frequency = request.form['watering_frequency']
        plant_type = request.form['plant_type']

        cur.execute(
            '''
            UPDATE plants
            SET name = %s,
                watering_frequency = %s,
                plant_type = %s
            WHERE id = %s
            ''',
            (name, watering_frequency, plant_type, plant_id)
        )

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for('index'))

    cur.execute(
        'SELECT * FROM plants WHERE id = %s',
        (plant_id,)
    )

    plant = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('edit_plant.html', plant=plant)


# Ruta para eliminar una planta
@app.route('/delete/<int:plant_id>', methods=('POST',))
def delete_plant(plant_id):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'DELETE FROM plants WHERE id = %s',
        (plant_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('index'))


# Ejecutar aplicación localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)