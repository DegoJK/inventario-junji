from flask import Blueprint, render_template, request, url_for, redirect, flash, session, jsonify
from db import mysql
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator

tipo_equipo = Blueprint("tipo_equipo", __name__, template_folder="app/templates")


# Definir el esquema de validación para tipo_equipo
tipo_equipo_schema = {
    'nombreTipo_Equipo': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
    }
}

# ruta para enviar los datos y visualizar la pagina principal para tipo de equipo
# Ruta para visualizar la página principal de tipos de equipo
@tipo_equipo.route("/tipo_equipo")
@tipo_equipo.route("/tipo_equipo/<int:page>")
@loguear_requerido
def tipoEquipo(page=1):
    if "user" not in session:
        flash("Se necesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")

    perpage = getPerPage()
    offset = (page - 1) * perpage

    cur = mysql.connection.cursor()

    # Obtener el total de registros para la paginación
    cur.execute("SELECT COUNT(*) AS total FROM tipo_equipo")
    total = cur.fetchone()["total"]

    # Obtener tipos de equipo con marcas relacionadas
    cur.execute("""
        SELECT 
            te.*, 
            GROUP_CONCAT(me.nombreMarcaEquipo SEPARATOR ', ') AS marcas
        FROM tipo_equipo te
        LEFT JOIN marca_tipo_equipo mte ON te.idTipo_equipo = mte.idTipo_equipo
        LEFT JOIN marca_equipo me ON mte.idMarca_Equipo = me.idMarca_Equipo
        GROUP BY te.idTipo_equipo
        LIMIT %s OFFSET %s
    """, (perpage, offset))
    tipo_equipo_data = cur.fetchall()

    # Obtener todas las marcas para el modal
    cur.execute("SELECT idMarca_equipo, nombreMarcaEquipo FROM marca_equipo")
    marcas = cur.fetchall()

    # Calcular última página
    lastpage = (total + perpage - 1) // perpage  # Redondeo hacia arriba

    return render_template(
        "Equipo/tipo_equipo.html",
        tipo_equipo=tipo_equipo_data,
        marcas=marcas,
        page=page,
        lastpage=page < lastpage
    )

# agrega un tipo de equipo
@tipo_equipo.route("/crear_tipo_equipo", methods=["GET", "POST"])
@administrador_requerido
def crear_tipo_equipo():
    if request.method == "POST":
        # Procesar datos del formulario
        nombreTipo_Equipo = request.form["nombreTipo_equipo"]
        marcas_seleccionadas = request.form.getlist("marcas[]")
        observacion = request.form.get("observacion", "")

        cur = mysql.connection.cursor()
        try:
            # Insertar el tipo de equipo
            cur.execute("""
                INSERT INTO tipo_equipo (nombreTipo_equipo, observacionTipoEquipo) 
                VALUES (%s, %s)
            """, (nombreTipo_Equipo, observacion))
            tipo_equipo_id = cur.lastrowid

            # Enlazar marcas seleccionadas
            for marca_id in marcas_seleccionadas:
                cur.execute("""
                    INSERT INTO marca_tipo_equipo (idMarca_Equipo, idTipo_equipo) 
                    VALUES (%s, %s)
                """, (marca_id, tipo_equipo_id))

            mysql.connection.commit()
            flash("Tipo de equipo creado correctamente.")
        except Exception as e:
            print(f"Error al crear tipo de equipo: {str(e)}")
            flash("Error al crear el tipo de equipo.")
            return redirect(url_for("tipo_equipo.tipoEquipo"))

        return redirect(url_for("tipo_equipo.tipoEquipo"))
    else:
        # Obtener todas las marcas para mostrarlas en el modal
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT idMarca_equipo, nombreMarcaEquipo 
            FROM marca_equipo
        """)
        marcas = cur.fetchall()
        return render_template(
            "Equipo/enlazar_marcas.html", 
            tipo_equipo=tipo_equipo, 
            marcas=marcas
        )


@tipo_equipo.route("/add_tipo_equipo/<idTipo_equipo>", methods=["POST"])
@administrador_requerido
def add_tipo_equipo(idTipo_equipo):
    print("idTipo_equipo:", idTipo_equipo)

    if request.method == "POST":
        try:
            # Obtener los datos del formulario
            marcas = request.form.getlist("marcas[]")
            observacion = request.form["observacion"]

            # Actualizar tipo_equipo
            cur = mysql.connection.cursor()
            cur.execute(
                """
                UPDATE tipo_equipo 
                SET observacionTipoEquipo = %s
                WHERE tipo_equipo.idTipo_equipo = %s
                """,
                (observacion, idTipo_equipo),
            )
            mysql.connection.commit()

            # Insertar marcas en marca_tipo_equipo
            for marca in marcas:
                print("Agregar marca:", marca)
                cur.execute(
                    """
                    INSERT INTO marca_tipo_equipo (idMarca_Equipo, idTipo_equipo)
                    VALUES (%s, %s)
                    """,
                    (marca, idTipo_equipo),
                )
            mysql.connection.commit()

            flash("Tipo de equipo agregado correctamente")
            return redirect(url_for("tipo_equipo.tipoEquipo"))

        except Exception as e:
            # Capturar y mostrar el error específico
            print("Error:", e)
            flash(f"Error al agregar tipo de equipo: {str(e)}")
            return redirect(url_for("tipo_equipo.tipoEquipo"))



@tipo_equipo.route("/update_tipo_equipo/<id>", methods=["POST"])
@administrador_requerido
def update_tipo_equipo(id):
    print("update tipo equipo")
    if request.method == "POST":
        data = {
            'nombreTipo_Equipo': request.form['nombreTipo_equipo']
        }
        ids_marca = request.form.getlist("marcas[]")
        print("ids_marca")
        print(ids_marca)

         # Validar los datos usando Cerberus
        v = Validator(tipo_equipo_schema)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for("tipo_equipo.tipoEquipo"))

        cur = mysql.connection.cursor()
        cur.execute(
            """
        SELECT * 
        FROM tipo_equipo 
        WHERE idTipo_equipo = %s
                    """,
            (id,),
        )
        tipo_equipo = cur.fetchone()
        cur.execute(
            """ 
        UPDATE tipo_equipo
        SET nombreTipo_equipo = %s
        WHERE idTipo_equipo = %s
        """,
            (data["nombreTipo_Equipo"], id),
        )
        #editar la relacion entre tipo y marcas
        cur.execute("""
        DELETE FROM marca_tipo_equipo
        WHERE idTipo_equipo = %s
        """, (id,))
        
        for id_marca in ids_marca:
            cur.execute("""
            INSERT INTO marca_tipo_equipo
            (idTipo_equipo, idMarca_Equipo)
            VALUES (%s, %s)
            """, (id,id_marca))
        mysql.connection.commit()
        return redirect(url_for("tipo_equipo.tipoEquipo"))



# elimina el registro segun el id
@tipo_equipo.route("/delete_tipo_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def delete_tipo_equipo(id):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            DELETE
            FROM marca_tipo_equipo
            WHERE marca_tipo_equipo.idTipo_equipo = %s
                    """,
            (id,),
        )
        cur.execute("DELETE FROM tipo_equipo WHERE idTipo_equipo = %s", (id,))
        mysql.connection.commit()
        flash("Tipo de equipo eliminado correctamente")
        return redirect(url_for("tipo_equipo.tipoEquipo"))
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for("tipo_equipo.tipoEquipo"))
