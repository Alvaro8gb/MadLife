# MadLife: Descubre los mejores eventos de Madrid
   [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://madlife.streamlit.app/)

<div>
    <img src="assets/logo.svg" alt="MadLife Logo" style="height: 200px; vertical-align: middle;" />
</div>

``MadLife`` surge como una herramienta inteligente que facilita la búsqueda de eventos en Madrid utilizando búsqueda semántica avanzada y tecnología de embeddings vectoriales para encontrar exactamente lo que buscas.

## Características

1. **Búsqueda semántica inteligente**: Utiliza embeddings vectoriales para encontrar eventos relevantes incluso con búsquedas en lenguaje natural.
   
2. **Visualización avanzada**: Dashboard interactivo con gráficos de similitud, distribución por distritos y análisis temporal.

3. **Filtrado multicriteria**: Filtra eventos por distrito, tipo, precio, fecha y otros metadatos relevantes.

4. **Exportación a calendario**: Integración directa con Google Calendar, Outlook, Yahoo Calendar y descarga de archivos ICS.



## Instalación

1. Clona el repositorio o descarga el código fuente.
2. Instala las dependencias de Python necesarias:

```bash
pip install -r requirements.txt
```

## Ejecutar la Aplicación

Para ejecutar la aplicación de Streamlit, navega al directorio del proyecto y ejecuta el siguiente comando:

```bash
streamlit run app.py
```

Esto iniciará el servidor de Streamlit y abrirá la aplicación en tu navegador predeterminado.

## Estructura de la Aplicación

### Módulos de funcionalidad (Frontend):
   Estos archivos y carpetas están relacionados con la interfaz de usuario y la presentación de datos:
   - **pages**: Contiene las páginas principales de la aplicación (búsqueda y detalles de eventos).
   - **core**: Módulos de visualización como gráficos, exportación de calendarios y resultados de búsqueda.

### Módulos de funcionalidad (Backend):
   Estos archivos manejan la lógica de negocio, acceso a datos y las operaciones de backend:
   - **app.py**: Archivo principal que ejecuta la aplicación Streamlit.
   - **config.py**: Configuraciones globales de la aplicación.
   - **utils.py**: Funciones utilitarias para procesamiento de datos.
   - **embedding_db.py**: Gestión de la base de datos vectorial y embeddings semánticos.
   - **apiManager.py**: Gestiona la carga de datos y APIs externas.
   - **chroma_db**: Base de datos vectorial para almacenamiento de embeddings.

### Metaarchivos de instalación y configuración:
   Estos archivos son usados para la instalación, configuración y documentación del proyecto:
   - **README.md**: Proporciona información sobre el proyecto, cómo instalarlo y cómo usarlo.
   - **Pipfile / Pipfile.lock**: Gestión de dependencias de Python con Pipenv.


## Datos

En el desarrollo de este proyecto se han utilizado los siguientes conjuntos de datos:

- **Portal de Datos Abiertos de Madrid**:
  - [**API de Eventos**](https://datos.madrid.es/): Sistema de información de eventos culturales y actividades de la ciudad de Madrid.


- **Tecnologías de Embeddings**:
  - **ChromaDB**: Base de datos vectorial para almacenamiento y búsqueda de embeddings.
  - **Sentence Transformers**: Modelos de lenguaje para generar embeddings semánticos de alta calidad.




## Mejoras Futuras

* [ ] RAG con LLM
* [ ] Favoritos de usuario y búsquedas guardadas
* [ ] Integración para compartir en redes sociales
* [ ] Análisis avanzado con insights de machine learning
* [ ] Mejoras en el diseño responsivo para dispositivos móviles
* [ ] Soporte multilingüe

## Contribuyendo

Al agregar nuevas funciones:

1. Seguir la estructura modular
2. Añadir la documentación correspondiente
3. Actualizar la configuración en `config.py`
4. Crear funciones auxiliares en `utils.py`
5. Probar exhaustivamente con diferentes tipos de eventos

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).

## Créditos

- **Fuente de Datos**: [Datos Abiertos de Madrid](https://datos.madrid.es/)
- **Librerías Usadas**: [Streamlit](https://streamlit.io/), [Pandas](https://pandas.pydata.org/), [Plotly](https://plotly.com/), [ChromaDB](https://www.trychroma.com/), [Sentence Transformers](https://www.sbert.net/)


