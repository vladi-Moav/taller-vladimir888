from conexion import *
import pytest
import requests

class Test_paises:

    def setup_class(self):
        self.url = "http://localhost:5082/paises"
        sql = "INSERT IGNORE INTO paises (idPais, nombre, continente) VALUES ('TP', 'Pais de Prueba', 'America')"
        mi_cursor.execute(sql)
        mi_db.commit()

    def teardown_class(self):
        sql = "DELETE FROM paises WHERE idPais='A12'"
        mi_cursor.execute(sql)
        mi_db.commit()

    def test_lista_paises(self):
        esperado = "paises"
        calculado = requests.get(self.url)
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == esperado

    @pytest.mark.parametrize(
        ["nuevo_entrada", "esperado_entrada"],
        [
            ({"id": "E21", "nombre": "Nuevo Pais", "continente": "Europa"}, "País agregado con éxito"),
            ({"id": "A12", "nombre": "Pais de Prueba", "continente": "America"}, "Id de país ya existe"),
        ]
    )
    def test_agregar(self, nuevo_entrada, esperado_entrada):
        calculado = requests.post(self.url, json=nuevo_entrada)
        assert calculado.status_code == 200
        assert esperado_entrada == calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [("A12", "País encontrado"), ("F31", "País no encontrado")]
    )
    def test_busqueda(self, id_entrada, esperado_entrada):
        calculado = requests.get(f"{self.url}/{id_entrada}")
        assert calculado.status_code == 200
        assert esperado_entrada in calculado.json()["mensaje"]

    def test_modifica1(self):
        id = "A12"
        nuevo = {"nombre": "Pais Modificado", "continente": "Asia"}
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        assert calculado.status_code == 200
        assert "País modificado con éxito" in calculado.json()["mensaje"]

    def test_modifica2(self):
        id = "AE"
        nuevo = {"nombre": "Nadie", "continente": "Oceania"}
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        assert calculado.status_code == 200
        assert "País no existe" in calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [("E21", "País eliminado con éxito!"), ("F31", "País no existe")]
    )
    def test_elimina(self, id_entrada, esperado_entrada):
        calculado = requests.delete(f"{self.url}/{id_entrada}")
        assert calculado.status_code == 200
        assert esperado_entrada in calculado.json()["mensaje"]
