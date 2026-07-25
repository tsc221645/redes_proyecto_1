# Redes - Proyecto 1
+ Ana Laura Tschen 221645

## Descripción del proyecto

Este proyecto consiste en el desarrollo de un chatbot empresarial orientado a apoyar a directivos y responsables de distintas áreas en el análisis de la operación de una organización. El chatbot permitirá realizar consultas en lenguaje natural sobre información almacenada en una base de datos empresarial, incluyendo datos relacionados con productos, ventas, inventarios y otros indicadores relevantes.

El sistema utilizará un modelo de lenguaje para interpretar las solicitudes del usuario y coordinar el acceso a herramientas externas mediante Model Context Protocol, MCP. Estas herramientas serán las responsables de consultar la base de datos, procesar la información y devolver resultados estructurados que puedan ser explicados de forma clara por el chatbot.

Además de responder consultas específicas, el sistema buscará facilitar la identificación de tendencias, variaciones entre periodos, productos con bajo rendimiento, posibles riesgos operativos y otras situaciones que puedan requerir atención. De esta manera, el chatbot funcionará como una herramienta de apoyo para el diagnóstico de la operación y la toma de decisiones basada en datos.

Como parte del proyecto, se implementará un servidor MCP personalizado que inicialmente se ejecutará de forma local y posteriormente será publicado como un servicio remoto. También se integrarán servidores MCP existentes para realizar operaciones relacionadas con el sistema de archivos y el control de versiones.

El proyecto incluirá el registro de las interacciones realizadas entre el chatbot y los servidores MCP, permitiendo analizar las solicitudes y respuestas intercambiadas mediante JSON-RPC. Asimismo, se considerarán mecanismos de seguridad para restringir el acceso a la información empresarial y evitar la exposición de datos sensibles.

## Tecnologías a utilizar

Las tecnologías propuestas para el desarrollo del proyecto son las siguientes:

* **Python:** lenguaje principal para desarrollar el chatbot, el cliente MCP y el servidor MCP personalizado.
* **SQL:** lenguaje utilizado internamente para consultar y procesar la información almacenada en la base de datos.
* **HTTP y HTTPS:** protocolos utilizados para la comunicación con el servidor MCP remoto y otros servicios externos.


## Contexto de la base de Datos
La base de datos proviene de una empresa real, por temas de confidencialidad, se anonimizaran ciertos resultados para proteger la integridad de los mismos.  La base de datos se levanta de manera local en una computadora personal, la cual tiene la capacidad de correrla sin ningun problema.

## Arquitectura