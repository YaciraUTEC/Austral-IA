# Austral IA: Piloto de Asistente Virtual de Mantenimiento y Proyectos de Energía

Este proyecto es un piloto funcional de un **asistente virtual especializado** en el área de mantenimiento y gestión de proyectos energéticos de **Austral Group**, desarrollado como parte del curso de Proyecto Preprofesional en la Universidad de Ingeniería y Tecnología (UTEC).

## Objetivo del Proyecto

Desarrollar e implementar un pilot asistente virtual capaz de automatizar tareas operativas, apoyar el diagnóstico técnico de fallas y centralizar el acceso a información técnica mediante tecnologías de **inteligencia artificial**, facilitando una toma de decisiones más ágil, eficiente y basada en datos.

## Objetivos SMART

- Automatizar al menos 3 procesos rutinarios de mantenimiento.
- Permitir la consulta técnica de al menos 5 equipos críticos.
- Reducir en más de un 30% el tiempo de búsqueda de información técnica.
- Garantizar una interfaz funcional desplegada y operativa.
- Completar el piloto en un plazo máximo de **16 semanas**.

## Tecnologías Utilizadas

- **Backend**: Python, FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Cloud Services (Azure)**:
  - OpenAI (GPT-4o, embeddings)
  - Azure AI Document Intelligence (Form Recognizer)
  - Azure Blob Storage
  - Azure Static Web Apps
  - Azure App Service
- **Búsqueda Semántica**: FAISS
- **Document Handling**:
  - LibreOffice (conversión DOCX a PDF)
  - pandas, openpyxl, xlrd (para Excel)

## Arquitectura del Sistema

El asistente sigue un flujo RAG (Retrieval-Augmented Generation):

1. Fragmentación de documentos (PDF, Word, Excel)
2. Extracción estructurada con Azure Form Recognizer
3. Embeddings semánticos con OpenAI
4. Indexación y búsqueda con FAISS
5. Respuestas generadas por GPT-4o con contexto técnico relevante



## Resultados

- 💬 Asistente funcional en entorno real con respuesta en lenguaje natural.
- 🧾 Consulta automatizada de documentos técnicos PDF, Word y Excel.
- 📉 Reducción del tiempo de acceso a información de 10-20 minutos a menos de 5 segundos.
- 👥 100% de aceptación en sesiones de prueba con personal técnico.



