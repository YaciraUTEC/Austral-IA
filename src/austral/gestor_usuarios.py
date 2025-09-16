# Importar librerías necesarias
from typing import List

# Clase para representar un usuario
class Usuario:
    def __init__(self, nombre: str, correo: str, contrasena: str):
        self.nombre = nombre
        self.correo = correo
        self.contrasena = contrasena
        self.historial = []  # Historial de preguntas y respuestas del usuario

    def agregar_interaccion(self, pregunta: str, respuesta: str):
        """
        Agregar una interacción al historial del usuario.
        """
        self.historial.append({"pregunta": pregunta, "respuesta": respuesta})

    def obtener_historial(self) -> List[dict]:
        """
        Obtener el historial completo del usuario.
        """
        return self.historial

# Clase para gestionar los usuarios
class GestorUsuarios:
    def __init__(self):
        self.usuarios = {}
        self._crear_usuarios_predeterminados()

    def _crear_usuarios_predeterminados(self):
        """
        Crear 5 usuarios predeterminados.
        """
        usuarios_predeterminados = [
            {"nombre": "Admin1", "correo": "admin1@ejemplo.com", "contrasena": "admin123"},
            {"nombre": "Usuario1", "correo": "usuario1@ejemplo.com", "contrasena": "usuario123"},
            {"nombre": "Usuario2", "correo": "usuario2@ejemplo.com", "contrasena": "usuario456"},
            {"nombre": "Usuario3", "correo": "usuario3@ejemplo.com", "contrasena": "usuario789"},
            {"nombre": "Usuario4", "correo": "usuario4@ejemplo.com", "contrasena": "usuario000"},
        ]
        for usuario in usuarios_predeterminados:
            self.crear_usuario(usuario["nombre"], usuario["correo"], usuario["contrasena"])

    def crear_usuario(self, nombre: str, correo: str, contrasena: str):
        """
        Crear un nuevo usuario.
        """
        if correo in self.usuarios:
            raise ValueError("El usuario con este correo ya existe.")
        self.usuarios[correo] = Usuario(nombre, correo, contrasena)

    def obtener_usuario(self, correo: str) -> Usuario:
        """
        Obtener un usuario por su correo.
        """
        if correo not in self.usuarios:
            raise ValueError("Usuario no encontrado.")
        return self.usuarios[correo]

    def autenticar_usuario(self, correo: str, contrasena: str) -> Usuario:
        """
        Autenticar un usuario por correo y contraseña.
        """
        print(f"Intentando autenticar usuario: {correo}")  # Registro de depuración
        if correo not in self.usuarios:
            print("Usuario no encontrado.")  # Registro de depuración
            raise ValueError("Usuario no encontrado.")
        
        usuario = self.usuarios[correo]
        if usuario.contrasena == contrasena:
            print("Autenticación exitosa.")  # Registro de depuración
            return usuario
        
        print("Contraseña incorrecta.")  # Registro de depuración
        raise ValueError("Credenciales incorrectas.")

