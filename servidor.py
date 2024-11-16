from flask import Flask, jsonify, request, Response
from functools import wraps
import os

app = Flask(__name__)

# Ruta del archivo de texto donde se guardarán los usuarios
ARCHIVO_USUARIOS = 'usuarios.txt'

# Función para cargar usuarios desde el archivo
def cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        return []
    with open(ARCHIVO_USUARIOS, 'r') as archivo:
        usuarios = []
        for linea in archivo:
            partes = linea.strip().split(',')
            if len(partes) == 2:
                usuarios.append({"id": int(partes[0]), "nombre": partes[1]})
        return usuarios

# Función para guardar usuarios en el archivo
def guardar_usuarios():
    with open(ARCHIVO_USUARIOS, 'w') as archivo:
        for usuario in base_datos["usuarios"]:
            archivo.write(f"{usuario['id']},{usuario['nombre']}\n")

# Base de datos simulada cargada desde el archivo
base_datos = {
    "usuarios": cargar_usuarios()
}

# Función para verificar la autenticación básica (se aplica a rutas protegidas)
def verificar_autenticacion(func):
    @wraps(func)
    def decorador(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != 'admin' or auth.password != 'secreto123':
            # Si no se autentica correctamente, se devuelve 401 (no autorizado)
            return Response('Acceso no autorizado', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return func(*args, **kwargs)
    return decorador

# Ruta para obtener todos los usuarios (protegida por autenticación básica)
@app.route('/usuarios', methods=['GET'])
@verificar_autenticacion
def obtener_usuarios():
    return jsonify(base_datos["usuarios"])

# Ruta para obtener un usuario por id (protegida por autenticación básica)
@app.route('/usuarios/<int:id>', methods=['GET'])
@verificar_autenticacion
def obtener_usuario(id):
    for usuario in base_datos["usuarios"]:
        if usuario["id"] == id:
            return jsonify(usuario)
    return jsonify({"error": "Usuario no encontrado"}), 404

# Ruta para agregar un usuario (sin autenticación)
@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    nombre = request.form.get('nombre')

    # Validar que el nombre se haya proporcionado
    if not nombre:
        return jsonify({"error": "Nombre no proporcionado"}), 400

    # Validar que el nombre no esté en uso
    for usuario in base_datos["usuarios"]:
        if usuario["nombre"] == nombre:
            return jsonify({"error": "Nombre de usuario ya existe"}), 409

    # Genera un nuevo ID basado en el número de usuarios actuales
    nuevo_id = len(base_datos["usuarios"]) + 1
    nuevo_usuario = {"id": nuevo_id, "nombre": nombre}
    base_datos["usuarios"].append(nuevo_usuario)  # Agrega el nuevo usuario

    # Guardar cambios en el archivo
    guardar_usuarios()

    return jsonify(nuevo_usuario), 201  # Retorna el usuario agregado con código 201

# Ruta para eliminar un usuario por id (protegida por autenticación básica)
@app.route('/usuarios/<int:id>', methods=['DELETE'])
@verificar_autenticacion
def eliminar_usuario(id):
    global base_datos
    usuario_a_eliminar = None
    for usuario in base_datos["usuarios"]:
        if usuario["id"] == id:
            usuario_a_eliminar = usuario
            break
    if usuario_a_eliminar:
        base_datos["usuarios"].remove(usuario_a_eliminar)

        # Guardar cambios en el archivo
        guardar_usuarios()

        return jsonify({"mensaje": f"Usuario con ID {id} eliminado correctamente"}), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Ejecuta el servidor en el puerto 5000
