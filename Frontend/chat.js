document.addEventListener('DOMContentLoaded', () => {
    // Elementos del DOM
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('user-query');
    const chatMessages = document.getElementById('chat-messages');
    const menuItems = document.querySelectorAll('.menu-item');
    const newChatBtn = document.querySelector('.new-chat');
    const sendButton = document.getElementById('send-button');
    const buttonIcon = sendButton.querySelector('.button-icon');

    // Controlador para abortar solicitudes
    let controladorAbort = null;

    // Función para crear el mensaje de loading
    function crearLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'mensaje asistente';
        loadingDiv.innerHTML = `
            <span class="mensaje-icono">🤖</span>
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p>Generando respuesta...</p>
            </div>
        `;
        return loadingDiv;
    }

    // Función para agregar mensajes
    function agregarMensaje(tipo, texto) {
        const mensajeDiv = document.createElement('div');
        mensajeDiv.className = `mensaje ${tipo}`;

        const icono = document.createElement('span');
        icono.className = 'mensaje-icono';
        icono.textContent = tipo === 'usuario' ? '👤' : tipo === 'asistente' ? '🤖' : '⚠️';
        
        const contenido = document.createElement('p');
        contenido.textContent = texto;

        mensajeDiv.appendChild(icono);
        mensajeDiv.appendChild(contenido);

        // Remover mensaje de bienvenida si existe
        const welcome = document.querySelector('.welcome');
        if (welcome) welcome.remove();

        chatMessages.appendChild(mensajeDiv);
        mensajeDiv.scrollIntoView({ behavior: 'smooth' });
    }

    // Función para manejar el clic en el botón de envío/detener
    async function manejarSubmit(e) {
        e.preventDefault();

        // Si hay una solicitud en curso, cancelarla
        if (controladorAbort) {
            controladorAbort.abort();
            controladorAbort = null;
            return;
        }

        const pregunta = chatInput.value.trim();
        if (!pregunta) return;

        // Crear nuevo controlador para esta solicitud
        controladorAbort = new AbortController();

        // Cambiar el icono a modo loading
        sendButton.classList.add('loading');
        buttonIcon.textContent = '⏹';
        
        // Mostrar pregunta del usuario
        agregarMensaje('usuario', pregunta);

        // Mostrar loading
        const loadingDiv = crearLoading();
        chatMessages.appendChild(loadingDiv);
        loadingDiv.scrollIntoView({ behavior: 'smooth' });

        // Deshabilitar input
        chatInput.value = '';
        chatInput.disabled = true;

        try {
            const response = await fetch('http://localhost:8000/api/asistente', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pregunta: pregunta }),
                signal: controladorAbort.signal
            });

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();
            
            // Remover loading y mostrar respuesta
            loadingDiv.remove();
            agregarMensaje('asistente', data.respuesta);

        } catch (error) {
            console.error('Error:', error);
            loadingDiv.remove();
            if (error.name === 'AbortError') {
                agregarMensaje('error', 'Generación de respuesta cancelada.');
            } else {
                agregarMensaje('error', 'Lo siento, hubo un error al procesar tu consulta.');
            }
        } finally {
            // Restaurar interfaz
            controladorAbort = null;
            sendButton.classList.remove('loading');
            buttonIcon.textContent = '➤';
            chatInput.disabled = false;
            chatInput.focus();
        }
    }

    // Event listeners
    chatForm.addEventListener('submit', manejarSubmit);

    // Nueva conversación
    newChatBtn.addEventListener('click', () => {
        chatMessages.innerHTML = '';
        const welcome = document.createElement('div');
        welcome.className = 'welcome';
        welcome.innerHTML = `
            <h1><span>Hola Yacira Nicol</span></h1>
            <p class="subtitle">Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?</p>
            <p class="description">Consulta rápida acerca de proyectos de energía.</p>
        `;
        chatMessages.parentElement.insertBefore(welcome, chatMessages);
    });

    // Manejar tecla Enter
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Resaltar ítem activo del menú
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });
});