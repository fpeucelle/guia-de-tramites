# Guía de Trámites - Sitio de Prueba

Este es un sitio de prueba para verificar datos cargados para la nueva página web de guía de trámites.

## Descripción

El sitio permite visualizar, buscar y filtrar información sobre diferentes trámites administrativos. Es una herramienta para verificar que los datos se cargan y muestran correctamente antes de la implementación en el sitio web principal.

## Características

- **Visualización de trámites**: Muestra todos los trámites disponibles en tarjetas informativas
- **Búsqueda**: Permite buscar trámites por nombre, descripción o requisitos
- **Filtros**: Filtrado por categoría de trámite
- **Estadísticas**: Muestra el total de trámites y categorías disponibles
- **Diseño responsivo**: Se adapta a diferentes tamaños de pantalla

## Estructura de Archivos

```
guia-de-tramites/
├── index.html      # Página principal del sitio
├── app.js          # Lógica de la aplicación (carga y visualización de datos)
├── styles.css      # Estilos del sitio
├── tramites.json   # Datos de ejemplo de trámites
└── README.md       # Este archivo
```

## Cómo Usar

### Opción 1: Servidor Local con Python

1. Abre una terminal en el directorio del proyecto
2. Ejecuta uno de los siguientes comandos según tu versión de Python:

```bash
# Python 3
python -m http.server 8000

# O Python 2
python -m SimpleHTTPServer 8000
```

3. Abre tu navegador y visita: `http://localhost:8000`

### Opción 2: Servidor Local con Node.js

1. Instala http-server si no lo tienes:
```bash
npm install -g http-server
```

2. En el directorio del proyecto, ejecuta:
```bash
http-server
```

3. Abre tu navegador en la URL mostrada (generalmente `http://localhost:8080`)

### Opción 3: Extensión de Navegador

Puedes usar extensiones como "Live Server" en Visual Studio Code o "Web Server for Chrome" para servir los archivos localmente.

## Datos de Prueba

El archivo `tramites.json` contiene datos de ejemplo con 10 trámites diferentes que incluyen:

- Obtención de DNI
- Licencia de Conducir
- Pasaporte
- Permiso de Obra
- Certificado de Antecedentes Penales
- Inscripción en Monotributo
- Registro de Marca
- Habilitación Comercial
- Certificado de Libre Deuda
- Permiso de Importación

Cada trámite incluye:
- Nombre
- Categoría
- Descripción
- Requisitos
- Costo
- Duración estimada
- Lugar donde realizar el trámite

## Cómo Agregar Nuevos Trámites

Para agregar nuevos trámites al sitio de prueba:

1. Abre el archivo `tramites.json`
2. Agrega un nuevo objeto en el array `tramites` siguiendo esta estructura:

```json
{
  "id": 11,
  "nombre": "Nombre del Trámite",
  "categoria": "Categoría",
  "descripcion": "Descripción breve del trámite",
  "requisitos": [
    "Requisito 1",
    "Requisito 2"
  ],
  "costo": "$XXX",
  "duracion": "XX días hábiles",
  "lugar": "Lugar donde realizarlo"
}
```

3. Guarda el archivo y recarga la página

## Funcionalidades de Búsqueda y Filtrado

- **Búsqueda por texto**: Escribe en el campo de búsqueda para encontrar trámites por nombre, descripción o requisitos
- **Filtro por categoría**: Usa el menú desplegable para filtrar por categoría específica
- **Combinación de filtros**: Puedes combinar la búsqueda de texto con el filtro de categoría

## Tecnologías Utilizadas

- HTML5
- CSS3
- JavaScript (ES6+)
- JSON para almacenamiento de datos

## Notas

- Este es un sitio de prueba estático que carga datos desde un archivo JSON local
- No requiere base de datos ni backend
- Los datos son de ejemplo y deben ser reemplazados con datos reales antes de la implementación en producción