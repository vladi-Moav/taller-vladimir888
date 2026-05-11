from conexion import *
import pytest
import requests

class Test_autores:

    def setup_class(self):
        self.url = "http://localhost:5081/autores"
        
        sql_pais = "INSERT IGNORE INTO paises (idPais, nombre, continente) VALUES ('CO', 'Colombia', 'America')"
        mi_cursor.execute(sql_pais)
        mi_db.commit()
        
        sql = "INSERT IGNORE INTO autores (idAutor, nombre, email, idPais) VALUES ('2215', 'Autor de Prueba', 'ejemplo@test.com', 'CO')"
        mi_cursor.execute(sql)
        mi_db.commit()


    def test_lista_autores(self):
        esperado = "autores"
        calculado = requests.get(self.url)
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == esperado

    @pytest.mark.parametrize(
        ["nuevo_entrada", "esperado_entrada"],
        [
            ({"id": "342", "nombre": "Nuevo Autor", "email": "ejemplo@test.com", "idPais": "CO"}, "Autor agregado con éxito"),
            ({"id": "2341", "nombre": "Autor de Prueba", "email": "ejemplo@test.com", "idPais": "CO"}, "Id de autor ya existe"),
        ]
    )
    def test_agregar(self, nuevo_entrada, esperado_entrada):
        calculado = requests.post(self.url, json=nuevo_entrada)
        assert calculado.status_code == 200
        assert esperado_entrada == calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [("342", "Autor encontrado"),
        ("N0",  "Autor no encontrado"),]
    )
    def test_busqueda(self, id_entrada, esperado_entrada):
        id = id_entrada
        esperado = esperado_entrada
        calculado = requests.get(f"{self.url}/{id}")
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

    def test_modifica1(self):
        id = "AU001"
        nombre = "Autor Modificado"
        email = "ejemplo@test.com"
        idPais = "CO"
        nuevo = {"nombre": nombre, "email": email, "idPais": idPais}
        esperado = "Autor modificado con éxito"
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]
        sql = f"SELECT * FROM autores WHERE idAutor='{id}'"
        mi_cursor.execute(sql)
        datos = mi_cursor.fetchall()[0]
        assert nombre == datos[1] and email == datos[2]

    def test_modifica2(self):
        id = "No"
        nuevo = {"nombre": "Estef", "email": "ejemplo@test.com", "idPais": "CO"}
        esperado = "Autor no existe"
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [("4232",    "Autor eliminado con éxito!"),
        ("No", "Autor no existe"),]
    )

    def test_elimina(self, id_entrada, esperado_entrada):
        id = id_entrada
        esperado = esperado_entrada
        calculado = requests.delete(f"{self.url}/{id}")
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

        if "éxito" in esperado_entrada:
            mi_db.commit()
            sql = f"SELECT * FROM autores WHERE idAutor='{id}'"
            mi_cursor.execute(sql)
            datos = mi_cursor.fetchall()
            assert len(datos) == 0
