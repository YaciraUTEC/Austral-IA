document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('user-query');
    const chatMessages = document.getElementById('chat-messages');
    const menuItems = document.querySelectorAll('.menu-item');
    const newChatBtn = document.querySelector('.new-chat');
    const sendButton = document.getElementById('send-button');
    const buttonIcon = sendButton.querySelector('.button-icon');
    const sidebar = document.querySelector('.sidebar');
    const menuIcon = document.querySelector('.menu-icon');

    menuIcon.style.cursor = 'pointer';
    menuIcon.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    let controladorAbort = null;

    // 🔐 IDENTIFICADOR DE USUARIO
    const userId = "usuario_test_1"; // Puedes cambiar esto dinámicamente si tienes login

    function crearLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'mensaje asistente';

        const icono = document.createElement('span');
        icono.className = 'mensaje-icono';

        const img = document.createElement('img');
        img.src = 'assets/IA.png';
        img.alt = 'Asistente';
        img.className = 'icono-imagen';
        icono.appendChild(img);

        const container = document.createElement('div');
        container.className = 'loading-container';

        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';

        const texto = document.createElement('div');
        texto.className = 'mensaje-contenido loading-dots';
        texto.innerHTML = 'Generando respuesta<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>';

        container.appendChild(spinner);
        container.appendChild(texto);

        loadingDiv.appendChild(icono);
        loadingDiv.appendChild(container);

        return loadingDiv;
    }

    function agregarMensaje(tipo, texto) {
        const mensajeDiv = document.createElement('div');
        mensajeDiv.className = `mensaje ${tipo}`;

        const icono = document.createElement('span');
        icono.className = 'mensaje-icono';

        if (tipo === 'asistente') {
            const img = document.createElement('img');
            img.src = 'assets/IA.png';
            img.alt = 'Asistente';
            img.className = 'icono-imagen';
            icono.appendChild(img);
        } else {
            icono.textContent = tipo === 'usuario' ? '👤' : '⚠️';
        }

        const contenido = document.createElement('div');
        contenido.classList.add('mensaje-contenido');

        const scrollWrapper = document.createElement('div');
        scrollWrapper.classList.add('tabla-scrollable');
        scrollWrapper.innerHTML = window.marked ? marked.parse(texto) : texto;

        contenido.appendChild(scrollWrapper);

        mensajeDiv.appendChild(icono);
        mensajeDiv.appendChild(contenido);

        const welcome = document.querySelector('.welcome');
        if (welcome) welcome.remove();

        chatMessages.appendChild(mensajeDiv);
        mensajeDiv.scrollIntoView({ behavior: 'smooth' });
    }

    async function manejarSubmit(e) {
        e.preventDefault();

        if (controladorAbort) {
            controladorAbort.abort();
            controladorAbort = null;
            return;
        }

        const pregunta = chatInput.value.trim();
        if (!pregunta) return;

        controladorAbort = new AbortController();

        sendButton.classList.add('loading');
        buttonIcon.textContent = '⏹';

        agregarMensaje('usuario', pregunta);

        const loadingDiv = crearLoading();
        chatMessages.appendChild(loadingDiv);
        loadingDiv.scrollIntoView({ behavior: 'smooth' });

        chatInput.value = '';
        chatInput.disabled = true;

        try {
            const response = await fetch('https://assistant-australia-dmangjedg6adffcu.brazilsouth-01.azurewebsites.net', {

                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, pregunta }), // Enviamos user_id también
                signal: controladorAbort.signal
            });

            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

            const data = await response.json();
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
            controladorAbort = null;
            sendButton.classList.remove('loading');
            buttonIcon.textContent = '➤';
            chatInput.disabled = false;
            chatInput.focus();
        }
    }

    chatForm.addEventListener('submit', manejarSubmit);

    newChatBtn.addEventListener('click', () => {
        // 🔁 Reiniciar conversación en backend
        fetch("http://localhost:8000/api/asistente/reiniciar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId })
        });

        // 💬 Limpiar mensajes en el frontend
        chatMessages.innerHTML = '';
        const existingWelcome = document.querySelector('.welcome');
        if (existingWelcome) existingWelcome.remove();

        const welcome = document.createElement('div');
        welcome.className = 'welcome';
        welcome.innerHTML = `
            <h1><span>Hola Yacira Nicol</span></h1>
            <p class="subtitle">Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?</p>
            <p class="description">Consulta rápida acerca de proyectos de energía.</p>
        `;
        chatMessages.parentElement.insertBefore(welcome, chatMessages);
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });
});
