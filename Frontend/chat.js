// Configuración de la API
const API_CONFIG = {
  baseUrl: 'asistentepiloto-g7adazdncyfzahh4.brazilsouth-01.azurewebsites.net',
  endpoints: {
    asistente: '/api/asistente',
    reiniciar: '/api/asistente/reiniciar',
    health: '/api/health'
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const welcome = document.getElementById("welcome");
  const mantenimientoSection = document.getElementById("mantenimiento-section");
  const proyectosSection = document.getElementById("proyectos-section");

  // Contenedores de chat
  const mantenimientoChat = document.getElementById("mantenimiento-chat");
  const proyectosChat = document.getElementById("proyectos-chat");

  // Formularios
  const mantenimientoForm = document.getElementById("mantenimiento-form");
  const proyectosForm = document.getElementById("proyectos-form");
  
  // Categoría activa
  let categoriaActiva = "mantenimiento";

  // Submenú
  const menuAsistente = document.getElementById("menu-asistente");
  const submenu = document.getElementById("submenu-asistente");
  const arrow = menuAsistente.querySelector(".arrow");

  const sideMantenimiento = document.getElementById("side-mantenimiento");
  const sideProyectos = document.getElementById("side-proyectos");
  
  // Función para mostrar secciones  
  function showSection(section) {
      welcome.style.display = "none";
      mantenimientoSection.style.display = "none";
      proyectosSection.style.display = "none";
      
      // Ocultar todas las áreas de chat
      const chatSection = document.getElementById('chat-section');
      if (chatSection) {
        chatSection.style.display = "none";
      }
      
      // Siempre ocultar ambos contenedores de chat primero
      if (mantenimientoChat) {
        mantenimientoChat.style.display = "none";
        mantenimientoChat.classList.remove("active");
      }
      if (proyectosChat) {
        proyectosChat.style.display = "none";
        proyectosChat.classList.remove("active");
      }
      
      // Ocultar el formulario persistente si existe
      const chatInputPersistente = document.getElementById('chat-input-persistente');
      if (chatInputPersistente) {
        chatInputPersistente.style.display = "none";
      }
  
      if (section === "welcome") {
        // Si es la pantalla de bienvenida, solo mostramos eso y salimos
        welcome.style.display = "block";
        return;
      }
      
      if (section === "mantenimiento") {
        categoriaActiva = "mantenimiento";
        
        // Asegurarse de que proyectos esté completamente oculto
        if (proyectosChat) {
          proyectosChat.style.display = "none";
          proyectosChat.classList.remove("active");
        }
        
        // Si hay conversación previa en mantenimiento, mostrarla
        if (mantenimientoChat && mantenimientoChat.childNodes.length > 0) {
          if (chatSection) chatSection.style.display = "block";
          mantenimientoChat.style.display = "flex";
          mantenimientoChat.classList.add("active");
          
          // Mostrar el formulario persistente y configurarlo para mantenimiento
          if (chatInputPersistente) {
            chatInputPersistente.style.display = "flex";
            
            const formPersistente = document.getElementById('chat-form-persistente');
            if (formPersistente) {
              formPersistente.dataset.categoria = "mantenimiento";
              
              const inputPersistente = document.getElementById('persistente-query');
              if (inputPersistente) {
                inputPersistente.placeholder = "🌐︎ Consulta sobre mantenimiento";
                setTimeout(() => inputPersistente.focus(), 100);
              }
            }
          }
        } else {
          // Si no hay conversación previa, mostrar la sección inicial
          mantenimientoSection.style.display = "block";
          
          // Restaurar el formulario de mantenimiento
          if (mantenimientoForm) {
            const input = mantenimientoForm.querySelector(".user-query");
            if (input) {
              input.value = "";
              setTimeout(() => input.focus(), 100);
            }
          }
        }
      }
      
      if (section === "proyectos") {
        categoriaActiva = "proyectos";
        
        // Asegurarse de que mantenimiento esté completamente oculto
        if (mantenimientoChat) {
          mantenimientoChat.style.display = "none";
          mantenimientoChat.classList.remove("active");
        }
        
        // Si hay conversación previa en proyectos, mostrarla
        if (proyectosChat && proyectosChat.childNodes.length > 0) {
          if (chatSection) chatSection.style.display = "block";
          proyectosChat.style.display = "flex";
          proyectosChat.classList.add("active");
          
          // Mostrar el formulario persistente y configurarlo para proyectos
          if (chatInputPersistente) {
            chatInputPersistente.style.display = "flex";
            
            const formPersistente = document.getElementById('chat-form-persistente');
            if (formPersistente) {
              formPersistente.dataset.categoria = "proyectos";
              
              const inputPersistente = document.getElementById('persistente-query');
              if (inputPersistente) {
                inputPersistente.placeholder = "🌐︎ Consulta sobre proyectos";
                setTimeout(() => inputPersistente.focus(), 100);
              }
            }
          }
        } else {
          // Si no hay conversación previa, mostrar la sección inicial
          proyectosSection.style.display = "block";
          
          // Restaurar el formulario de proyectos
          if (proyectosForm) {
            const input = proyectosForm.querySelector(".user-query");
            if (input) {
              input.value = "";
              setTimeout(() => input.focus(), 100);
            }
          }
        }
      }
    }

  // Menú lateral toggle
  menuAsistente.addEventListener("click", () => {
    submenu.classList.toggle("oculto");
    arrow.textContent = submenu.classList.contains("oculto") ? "▼" : "▲"; // Cambiar el icono dinámicamente
    arrow.style.marginLeft = submenu.classList.contains("oculto") ? "0px" : "-10px"; // Mover el icono más a la izquierda
  });
  // Submenú clics
  sideMantenimiento.addEventListener("click", () => {
    showSection("mantenimiento");
    sideMantenimiento.classList.add("active");
    sideProyectos.classList.remove("active");
    arrow.textContent = "▲"; // Actualizar el icono al desplegar la sección
    arrow.style.marginLeft = "-10px"; // Mover el icono más a la izquierda
  });
  sideProyectos.addEventListener("click", () => {
    showSection("proyectos");
    sideProyectos.classList.add("active");
    sideMantenimiento.classList.remove("active");
    arrow.textContent = "▲"; // Actualizar el icono al desplegar la sección
    arrow.style.marginLeft = "-10px"; // Mover el icono más a la izquierda
     const dots = document.querySelectorAll(".dot");
  dots.forEach(dot => dot.classList.add("stop-blink"));
  });

  // Vincular los formularios de consulta con sus manejadores
  if (mantenimientoForm) {
    mantenimientoForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = mantenimientoForm.querySelector(".user-query");
      const consulta = input.value.trim();
      
      if (consulta) {
        enviarConsulta(consulta, "mantenimiento");
        input.value = "";
      }
    });
  }
  
  if (proyectosForm) {
    proyectosForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = proyectosForm.querySelector(".user-query");
      const consulta = input.value.trim();
      
      if (consulta) {
        enviarConsulta(consulta, "proyectos");
        input.value = "";
      }
    });
  }  // Función para añadir mensaje al chat
  function addMessage(chatContainer, text, isUser = false) {
    console.log(`Añadiendo mensaje a ${chatContainer.id}, isUser: ${isUser}, texto: ${text.substring(0, 20)}...`);
    
    // Asegurarse que el contenedor esté visible
    chatContainer.style.display = "flex";
    
    const messageDiv = document.createElement("div");
    messageDiv.className = `mensaje ${isUser ? "usuario" : "asistente"}`;
    
    if (!isUser) {
      const iconDiv = document.createElement("div");
      iconDiv.className = "mensaje-icono";
      const iconImg = document.createElement("img");
      iconImg.src = "assets/IA.png"; // Icono del asistente
      iconImg.alt = "Asistente Icon";
      iconImg.className = "icono-imagen"; // Estilo para el icono
      iconDiv.appendChild(iconImg);
      messageDiv.appendChild(iconDiv);
    }
    
    const contentDiv = document.createElement("div");
    contentDiv.className = "mensaje-contenido";
    
    if (isUser) {
      contentDiv.textContent = text;
    } else {
      // Convertir markdown a HTML para mensajes del asistente
      try {
        contentDiv.innerHTML = marked.parse(text);
      } catch (e) {
        console.error("Error parsing markdown:", e);
        contentDiv.textContent = text;
      }
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Forzar reflow para asegurar que los nuevos elementos se rendericen correctamente
    chatContainer.offsetHeight;
    
    // Scroll al final del chat con un pequeño retraso para asegurar que todo esté renderizado
    setTimeout(() => {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 50);
  }// Función para crear el indicador de carga
  function crearLoading(chatContainer) {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'mensaje asistente';

    const iconDiv = document.createElement('div');
    iconDiv.className = 'mensaje-icono';

    const iconImg = document.createElement('img');
    iconImg.src = 'assets/IA.png';
    iconImg.alt = 'Asistente';
    iconImg.className = 'icono-imagen';
    iconDiv.appendChild(iconImg);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'mensaje-contenido';
    contentDiv.innerHTML = 'Generando respuesta<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>';

    // Añadir animación a los puntos
    const style = document.createElement('style');
    style.textContent = `
      @keyframes blink {
        0% { opacity: 0; }
        50% { opacity: 1; }
        100% { opacity: 0; }
      }
      .dot:nth-child(1) {
        animation: blink 1.5s infinite;
        animation-delay: 0s;
      }
      .dot:nth-child(2) {
        animation: blink 1.5s infinite;
        animation-delay: 0.5s;
      }
      .dot:nth-child(3) {
        animation: blink 1.5s infinite;
        animation-delay: 1s;
      }
    `;
    document.head.appendChild(style);
    
    loadingDiv.appendChild(iconDiv);
    loadingDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return loadingDiv;
  }// Controlador para cancelar solicitudes
  let controladorAbort = null;  // Función para enviar consulta al backend
  async function enviarConsulta(consulta, categoria) {
      console.log(`Enviando consulta en categoría: ${categoria}`);
      const chatContainer = categoria === "mantenimiento" ? mantenimientoChat : proyectosChat;
      
      // Si hay una solicitud en curso, cancelarla
      if (controladorAbort) {
        controladorAbort.abort();
        controladorAbort = null;
      }
      
      // Crear nuevo controlador para esta solicitud
      controladorAbort = new AbortController();
      
      // Verificar si existe el chat-section, si no, trabajamos directo con los contenedores
      const chatSection = document.getElementById('chat-section');
      
      // Ocultar el contenedor que no corresponde a esta categoría
      if (categoria === "mantenimiento") {
        if (proyectosChat) {
          proyectosChat.style.display = "none";
          proyectosChat.classList.remove("active");
        }
      } else if (categoria === "proyectos") {
        if (mantenimientoChat) {
          mantenimientoChat.style.display = "none";
          mantenimientoChat.classList.remove("active");
        }
      }
      
      // Activar solo el contenedor correspondiente a la categoría
      chatContainer.style.display = "flex";
      chatContainer.classList.add("active");
      
      // Actualizar la categoría activa
      categoriaActiva = categoria;
      
      // Ocultar la sección inicial correspondiente a la categoría
      if (categoria === "mantenimiento") {
        mantenimientoSection.style.display = "none";
        
        // Limpiar el campo de entrada de mantenimiento
        const mantenimientoInput = document.querySelector('#mantenimiento-form .user-query');
        if (mantenimientoInput) mantenimientoInput.value = '';
        
      } else if (categoria === "proyectos") {
        proyectosSection.style.display = "none";
        
        // Limpiar el campo de entrada de proyectos
        const proyectosInput = document.querySelector('#proyectos-form .user-query');
        if (proyectosInput) proyectosInput.value = '';
      }
      
      // Si existe chat-section, mostrarlo
      if (chatSection) {
        chatSection.style.display = "block";
      }
      
      // Mostrar mensaje del usuario en el contenedor específico
      addMessage(chatContainer, consulta, true);
      
      // Mostrar el formulario persistente después de la primera consulta
      mostrarFormularioPersistente(categoria);
      
      // Mostrar indicador de carga en el contenedor específico
      const loadingDiv = crearLoading(chatContainer);
      
      try {
        // 🔐 ID de usuario (podrías hacerlo dinámico si tienes login)
        const userId = "usuario_test_1";
        
        console.log(`Enviando consulta a la API con categoría: ${categoria}`);
        
        // URL del endpoint usando la configuración central
        const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.asistente}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            user_id: userId,
            pregunta: consulta,
            categoria: categoria  // Asegurarse de que la categoría se envíe correctamente
          }),
          signal: controladorAbort.signal
        });
          console.log('Respuesta del servidor:', response);
        
        if (!response.ok) {
          console.error('Error en la respuesta:', response.status, response.statusText);
          throw new Error(`Error en la solicitud: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        // Eliminar indicador de carga
        loadingDiv.remove();
        
        // Verificar si la respuesta indica que no hay información en la categoría
        const respuesta = data.respuesta || "No se recibió una respuesta válida";
        
        // Mostrar respuesta del asistente
        addMessage(chatContainer, respuesta);
        
      } catch (error) {
        console.error('Error al procesar la consulta:', error);
        
        // Eliminar indicador de carga
        if (loadingDiv && loadingDiv.parentNode) {
          loadingDiv.remove();
        }
        
        // Mostrar mensaje de error apropiado
        if (error.name === 'AbortError') {
          addMessage(chatContainer, "Generación de respuesta cancelada.");
        } else {
          addMessage(chatContainer, "Lo siento, ocurrió un error al procesar tu consulta. Por favor intenta nuevamente.");
        }
      } finally {
        controladorAbort = null;
      }
    }
  // Función para reiniciar la conversación
  async function reiniciarConversacion() {
    try {
      const userId = "usuario_test_1";
      
      const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.reiniciar}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          user_id: userId
        }),
      });
      
      if (response.ok) {
        console.log('Conversación reiniciada correctamente');
      } else {
        console.error('Error al reiniciar la conversación:', response.status);
      }
    } catch (error) {
      console.error('Error al reiniciar la conversación:', error);
    }
  }
  // Asociar el botón de nueva conversación con la función de reinicio
  const newChatBtn = document.querySelector('.new-chat');
  if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
      // Reiniciar conversación en el backend
      reiniciarConversacion();
      
      // Limpiar chats en la interfaz
      if (mantenimientoChat) {
        mantenimientoChat.innerHTML = '';
        mantenimientoChat.style.display = "none";
        mantenimientoChat.classList.remove("active");
      }
      
      if (proyectosChat) {
        proyectosChat.innerHTML = '';
        proyectosChat.style.display = "none";
        proyectosChat.classList.remove("active");
      }
      
      // Ocultar el formulario persistente si existe
      const chatInputPersistente = document.getElementById('chat-input-persistente');
      if (chatInputPersistente) {
        chatInputPersistente.style.display = "none";
      }
      
      // Mostrar la pantalla de bienvenida
      showSection('welcome');
    });
  }

  // Función para limpiar todos los campos de entrada
  function limpiarCamposEntrada() {
    // Limpiar campo de mantenimiento
    const mantenimientoInput = document.querySelector('#mantenimiento-form .user-query');
    if (mantenimientoInput) mantenimientoInput.value = '';
    
    // Limpiar campo de proyectos
    const proyectosInput = document.querySelector('#proyectos-form .user-query');
    if (proyectosInput) proyectosInput.value = '';
    
    // Limpiar campo persistente
    const inputPersistente = document.getElementById('persistente-query');
    if (inputPersistente) inputPersistente.value = '';
  }
  
  // Añadir evento al botón de nueva conversación para limpiar campos
  const newChatButton = document.querySelector('.new-chat');
  if (newChatButton) {
    newChatButton.addEventListener('click', limpiarCamposEntrada);
  }
  
  // Añadir evento a los elementos del menú para limpiar campos al cambiar de sección
  const menuItems = document.querySelectorAll('.submenu-item');
  menuItems.forEach(item => {
    item.addEventListener('click', limpiarCamposEntrada);
  });

  // Verificar conectividad con el backend al cargar
  async function verificarBackend() {
    try {
      const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.health}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        console.log('Conexión con el backend establecida correctamente');
        return true;
      } else {
        console.error('Error al conectar con el backend:', response.status);
        return false;
      }
    } catch (error) {
      console.error('No se pudo conectar con el backend:', error);
      return false;
    }
  }

  // Intentar verificar el backend al cargar la página
  verificarBackend().then(conectado => {
    if (!conectado) {
      console.warn('No se pudo establecer conexión con el backend. Algunas funciones pueden no estar disponibles.');
    }
  });
  
  // Función para expandir el área de chat cuando se realiza una pregunta
  function expandChatSection(chatContainer) {
    const parentSection = chatContainer.closest('.welcome2');
    if (parentSection) {
      parentSection.classList.add('chat-active');
      
      // Ocultar el título y la descripción
      const title = parentSection.querySelector('h1');
      const description = parentSection.querySelector('.description');
      
      if (title) title.style.display = 'none';
      if (description) description.style.display = 'none';
      
      // Expandir el contenedor de chat
      chatContainer.style.maxHeight = '75vh';
      chatContainer.style.minHeight = '500px';
    }
  }
    // Función para asegurar separación entre los chats de mantenimiento y proyectos
  function inicializarSeparacionChats() {
    // Obtener referencias a los elementos DOM
    const mantenimientoChat = document.getElementById("mantenimiento-chat");
    const proyectosChat = document.getElementById("proyectos-chat");
    const mantenimientoForm = document.getElementById("mantenimiento-form");
    const proyectosForm = document.getElementById("proyectos-form");
    
    if (!mantenimientoChat || !proyectosChat) {
      console.error("No se encontraron los contenedores de chat");
      return;
    }
      // Asegurarnos que los event listeners estén correctamente configurados
    if (mantenimientoForm) {
      mantenimientoForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const input = mantenimientoForm.querySelector(".user-query");
        if (input && input.value.trim()) {
          const textoConsulta = input.value.trim();
          
          // Ocultar proyectos-chat y activar mantenimiento-chat
          if (proyectosChat) {
            proyectosChat.style.display = "none";
            proyectosChat.classList.remove("active");
          }
          
          mantenimientoChat.style.display = "block";
          mantenimientoChat.classList.add("active");
          
          // Limpiar el campo inmediatamente antes de enviar la consulta
          input.value = "";
          
          enviarConsulta(textoConsulta, "mantenimiento");
        }
      });
    }
    
    if (proyectosForm) {
      proyectosForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const input = proyectosForm.querySelector(".user-query");
        if (input && input.value.trim()) {
          const textoConsulta = input.value.trim();
          
          // Ocultar mantenimiento-chat y activar proyectos-chat
          if (mantenimientoChat) {
            mantenimientoChat.style.display = "none";
            mantenimientoChat.classList.remove("active");
          }
          
          proyectosChat.style.display = "block";
          proyectosChat.classList.add("active");
          
          // Limpiar el campo inmediatamente antes de enviar la consulta
          input.value = "";
          
          enviarConsulta(textoConsulta, "proyectos");
        }
      });
    }
      // Asegurarnos que cuando cambiamos de sección, los chats se muestran/ocultan correctamente
    const sideMantenimiento = document.getElementById("side-mantenimiento");
    const sideProyectos = document.getElementById("side-proyectos");
    
    if (sideMantenimiento) {
      sideMantenimiento.addEventListener("click", () => {
        // Al cambiar a mantenimiento, asegurar que se oculta completamente el chat de proyectos
        if (proyectosChat) {
          proyectosChat.style.display = "none";
          proyectosChat.classList.remove("active");
        }
        
        // Solo mostrar el chat de mantenimiento si tiene contenido
        if (mantenimientoChat && mantenimientoChat.childNodes.length > 0) {
          mantenimientoChat.style.display = "block";
          mantenimientoChat.classList.add("active");
        }
      });
    }
    
    if (sideProyectos) {
      sideProyectos.addEventListener("click", () => {
        // Al cambiar a proyectos, asegurar que se oculta completamente el chat de mantenimiento
        if (mantenimientoChat) {
          mantenimientoChat.style.display = "none";
          mantenimientoChat.classList.remove("active");
        }
        
        // Solo mostrar el chat de proyectos si tiene contenido
        if (proyectosChat && proyectosChat.childNodes.length > 0) {
          proyectosChat.style.display = "block";
          proyectosChat.classList.add("active");
        }
      });
    }
  }

  // Inicializar separación de chats cuando el DOM esté completamente cargado
  document.addEventListener('DOMContentLoaded', inicializarSeparacionChats);
  
  // Función para depuración que verifica la visibilidad de los contenedores
  function verificarVisibilidad() {
    console.log("Estado actual de los contenedores:");
    const mantenimientoChat = document.getElementById("mantenimiento-chat");
    const proyectosChat = document.getElementById("proyectos-chat");
    
    if (mantenimientoChat) {
      console.log(`Mantenimiento chat - display: ${mantenimientoChat.style.display}, contiene ${mantenimientoChat.childNodes.length} mensajes`);
    } else {
      console.log("Contenedor mantenimiento-chat no encontrado");
    }
    
    if (proyectosChat) {
      console.log(`Proyectos chat - display: ${proyectosChat.style.display}, contiene ${proyectosChat.childNodes.length} mensajes`);
    } else {
      console.log("Contenedor proyectos-chat no encontrado");
    }
  }
  
  // Ejecutar verificación al cargar y periódicamente
  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(verificarVisibilidad, 1000);
  });
    // Función para mostrar el formulario persistente
  function mostrarFormularioPersistente(categoria) {
    const chatInputPersistente = document.getElementById('chat-input-persistente');
    if (!chatInputPersistente) return;
    
    // Mostrar el formulario persistente
    chatInputPersistente.style.display = 'flex';
    
    // Ajustar el contenedor de chat para dejar espacio al formulario
    const chatContainer = categoria === "mantenimiento" ? mantenimientoChat : proyectosChat;
    if (chatContainer) {
      chatContainer.classList.add('with-persistente');
    }
    
    // Configurar el formulario persistente para la categoría actual
    const formPersistente = document.getElementById('chat-form-persistente');
    if (formPersistente) {
      // Almacenar la categoría actual como un atributo de datos
      formPersistente.dataset.categoria = categoria;
      
      // Actualizar el placeholder según la categoría
      const inputPersistente = document.getElementById('persistente-query');
      if (inputPersistente) {
        inputPersistente.placeholder = categoria === "mantenimiento" 
          ? "🌐︎ Consulta sobre mantenimiento" 
          : "🌐︎ Consulta sobre proyectos";
      }
      
      // Eliminar listeners previos para evitar duplicados
      const nuevoForm = formPersistente.cloneNode(true);
      formPersistente.parentNode.replaceChild(nuevoForm, formPersistente);
      
      // Añadir el listener al nuevo formulario
      nuevoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const inputPersistente = document.getElementById('persistente-query');
        if (inputPersistente && inputPersistente.value.trim()) {
          const consulta = inputPersistente.value.trim();
          // Obtener la categoría almacenada
          const categoriaActual = nuevoForm.dataset.categoria || categoria;
          // Limpiar el campo inmediatamente antes de procesar
          inputPersistente.value = '';
          // Hacer focus de nuevo en el input para facilitar más consultas
          setTimeout(() => inputPersistente.focus(), 100);
          // Enviar la consulta con la categoría correcta
          enviarConsulta(consulta, categoriaActual);
        }
      });
    }
  }
  
  // Ajustar el formulario persistente cuando se colapsa o expande el sidebar
  const menuIcon = document.querySelector('.menu-icon');
  if (menuIcon) {
    menuIcon.addEventListener('click', function() {
      const sidebar = document.querySelector('.sidebar');
      const chatInputPersistente = document.getElementById('chat-input-persistente');
      
      if (sidebar && chatInputPersistente) {
        if (sidebar.classList.contains('collapsed')) {
          chatInputPersistente.style.left = '60px'; // Sidebar colapsado
        } else {
          chatInputPersistente.style.left = '280px'; // Sidebar expandido
        }
      }
    });
  }
});
