/**
 * Chatbot Widget - Dispusipda Pekanbaru
 * Standalone JavaScript file untuk di-embed ke website PHP
 * 
 * Cara penggunaan:
 * 1. Tambahkan script ini ke halaman PHP Anda
 * 2. Panggil ChatbotWidget.init({ apiUrl: 'YOUR_API_URL' })
 */

(function() {
    'use strict';

    // Cek apakah sudah ada instance
    if (window.ChatbotWidget) return;

    // ==================== DEFAULT CONFIG ====================
    const DEFAULT_CONFIG = {
        apiUrl: 'http://localhost:5000',
        position: 'right', // 'right' atau 'left'
        primaryColor: '#1e88e5',
        greetingAutoCloseDelay: 8000,
        greetingMessage: 'Halo! 👋 Ada yang bisa saya bantu tentang layanan perpustakaan?',
        headerTitle: 'Asisten Dispusipda',
        headerSubtitle: 'Online',
        placeholder: 'Ketik pertanyaan Anda...',
        suggestions: [
            'Cara mendaftar anggota?',
            'Jam buka perpustakaan?',
            'Layanan yang tersedia?'
        ]
    };

    // ==================== STYLES ====================
    const styles = `
        .dsp-chatbot-bubble {
            position: fixed;
            bottom: 24px;
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, var(--dsp-primary), var(--dsp-primary-dark));
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
            z-index: 9999;
            border: none;
            outline: none;
        }
        .dsp-chatbot-bubble.right { right: 24px; }
        .dsp-chatbot-bubble.left { left: 24px; }
        .dsp-chatbot-bubble:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(30, 136, 229, 0.4);
        }
        .dsp-chatbot-bubble svg {
            width: 32px;
            height: 32px;
            fill: white;
        }
        .dsp-chatbot-bubble.active .dsp-chat-icon { display: none; }
        .dsp-chatbot-bubble .dsp-close-icon { display: none; }
        .dsp-chatbot-bubble.active .dsp-close-icon { display: block; }

        .dsp-chatbot-greeting {
            position: fixed;
            bottom: 100px;
            background: white;
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            max-width: 280px;
            z-index: 9998;
            animation: dspSlideIn 0.3s ease;
            display: none;
        }
        .dsp-chatbot-greeting.right { right: 24px; }
        .dsp-chatbot-greeting.left { left: 24px; }
        .dsp-chatbot-greeting.show { display: block; }
        .dsp-chatbot-greeting p {
            margin: 0;
            color: #333;
            font-size: 14px;
            line-height: 1.5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .dsp-chatbot-greeting .dsp-close-greeting {
            position: absolute;
            top: 8px;
            right: 8px;
            background: none;
            border: none;
            cursor: pointer;
            color: #666;
            font-size: 18px;
            line-height: 1;
            padding: 4px;
        }
        .dsp-chatbot-greeting::after {
            content: '';
            position: absolute;
            bottom: -8px;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 8px solid white;
        }
        .dsp-chatbot-greeting.right::after { right: 24px; }
        .dsp-chatbot-greeting.left::after { left: 24px; }

        .dsp-chatbot-window {
            position: fixed;
            bottom: 100px;
            width: 380px;
            height: 520px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 9998;
            animation: dspSlideUp 0.3s ease;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .dsp-chatbot-window.right { right: 24px; }
        .dsp-chatbot-window.left { left: 24px; }
        .dsp-chatbot-window.open { display: flex; }

        @keyframes dspSlideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes dspSlideIn {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes dspFadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .dsp-chatbot-header {
            background: linear-gradient(135deg, var(--dsp-primary), var(--dsp-primary-dark));
            color: white;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .dsp-chatbot-header-avatar {
            width: 44px;
            height: 44px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .dsp-chatbot-header-avatar svg {
            width: 24px;
            height: 24px;
            fill: white;
        }
        .dsp-chatbot-header-info { flex: 1; }
        .dsp-chatbot-header-title {
            font-weight: 600;
            font-size: 16px;
            margin: 0;
        }
        .dsp-chatbot-header-status {
            font-size: 12px;
            opacity: 0.9;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .dsp-chatbot-header-status::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #4caf50;
            border-radius: 50%;
        }

        .dsp-chatbot-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .dsp-chatbot-messages::-webkit-scrollbar { width: 6px; }
        .dsp-chatbot-messages::-webkit-scrollbar-track { background: transparent; }
        .dsp-chatbot-messages::-webkit-scrollbar-thumb {
            background: #e0e0e0;
            border-radius: 3px;
        }

        .dsp-chat-message {
            display: flex;
            gap: 8px;
            max-width: 85%;
            animation: dspFadeIn 0.3s ease;
        }
        .dsp-chat-message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        .dsp-chat-message.bot { align-self: flex-start; }
        .dsp-chat-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: var(--dsp-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .dsp-chat-message.user .dsp-chat-avatar { background: #666; }
        .dsp-chat-avatar svg {
            width: 18px;
            height: 18px;
            fill: white;
        }
        .dsp-chat-bubble {
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
        }
        .dsp-chat-message.user .dsp-chat-bubble {
            background: var(--dsp-primary);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .dsp-chat-message.bot .dsp-chat-bubble {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .dsp-typing-indicator {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .dsp-typing-indicator span {
            width: 8px;
            height: 8px;
            background: var(--dsp-primary-light);
            border-radius: 50%;
            animation: dspTyping 1.4s infinite;
        }
        .dsp-typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .dsp-typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes dspTyping {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-8px); }
        }

        .dsp-chat-suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 12px 16px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        .dsp-suggestion-btn {
            padding: 8px 14px;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 12px;
            color: #333;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        .dsp-suggestion-btn:hover {
            background: var(--dsp-primary);
            color: white;
            border-color: var(--dsp-primary);
        }

        .dsp-chatbot-input {
            padding: 16px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 12px;
            align-items: center;
        }
        .dsp-chatbot-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 24px;
            font-size: 14px;
            outline: none;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        .dsp-chatbot-input input:focus {
            border-color: var(--dsp-primary);
            box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
        }
        .dsp-chatbot-input input::placeholder { color: #666; }
        .dsp-send-btn {
            width: 44px;
            height: 44px;
            background: var(--dsp-primary);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        .dsp-send-btn:hover { background: var(--dsp-primary-dark); }
        .dsp-send-btn:disabled {
            background: #e0e0e0;
            cursor: not-allowed;
        }
        .dsp-send-btn svg {
            width: 20px;
            height: 20px;
            fill: white;
        }

        .dsp-chatbot-powered {
            padding: 8px;
            text-align: center;
            font-size: 11px;
            color: #666;
            background: #f5f5f5;
        }

        @media (max-width: 480px) {
            .dsp-chatbot-window {
                width: calc(100% - 16px);
                height: calc(100% - 120px);
                right: 8px !important;
                left: 8px !important;
                bottom: 80px;
                border-radius: 12px;
            }
            .dsp-chatbot-bubble {
                width: 56px;
                height: 56px;
                bottom: 16px;
            }
            .dsp-chatbot-bubble.right { right: 16px; }
            .dsp-chatbot-bubble.left { left: 16px; }
            .dsp-chatbot-greeting {
                right: 16px !important;
                left: 16px !important;
                bottom: 84px;
                max-width: calc(100% - 80px);
            }
        }
    `;

    // ==================== CHATBOT WIDGET CLASS ====================
    class ChatbotWidget {
        constructor(config = {}) {
            this.config = { ...DEFAULT_CONFIG, ...config };
            this.state = {
                isOpen: false,
                sessionId: null,
                isTyping: false,
                greetingShown: false
            };
            this.elements = {};
            
            this.init();
        }

        init() {
            this.injectStyles();
            this.createElements();
            this.attachEventListeners();
            this.initSession();
            this.showGreetingAfterDelay();
        }

        injectStyles() {
            // Set CSS variables
            const root = document.documentElement;
            root.style.setProperty('--dsp-primary', this.config.primaryColor);
            root.style.setProperty('--dsp-primary-dark', this.darkenColor(this.config.primaryColor, 20));
            root.style.setProperty('--dsp-primary-light', this.lightenColor(this.config.primaryColor, 20));

            // Inject stylesheet
            if (!document.getElementById('dsp-chatbot-styles')) {
                const styleSheet = document.createElement('style');
                styleSheet.id = 'dsp-chatbot-styles';
                styleSheet.textContent = styles;
                document.head.appendChild(styleSheet);
            }
        }

        createElements() {
            const position = this.config.position;

            // Container
            const container = document.createElement('div');
            container.id = 'dsp-chatbot-container';

            // Bubble button
            container.innerHTML = `
                <button class="dsp-chatbot-bubble ${position}" id="dsp-chatbot-toggle">
                    <svg class="dsp-chat-icon" viewBox="0 0 24 24">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                        <path d="M7 9h10v2H7zm0-3h10v2H7zm0 6h7v2H7z"/>
                    </svg>
                    <svg class="dsp-close-icon" viewBox="0 0 24 24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>

                <div class="dsp-chatbot-greeting ${position}" id="dsp-chatbot-greeting">
                    <button class="dsp-close-greeting">&times;</button>
                    <p>${this.config.greetingMessage}</p>
                </div>

                <div class="dsp-chatbot-window ${position}" id="dsp-chatbot-window">
                    <div class="dsp-chatbot-header">
                        <div class="dsp-chatbot-header-avatar">
                            <svg viewBox="0 0 24 24">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                            </svg>
                        </div>
                        <div class="dsp-chatbot-header-info">
                            <h3 class="dsp-chatbot-header-title">${this.config.headerTitle}</h3>
                            <span class="dsp-chatbot-header-status">${this.config.headerSubtitle}</span>
                        </div>
                    </div>

                    <div class="dsp-chatbot-messages" id="dsp-chatbot-messages"></div>

                    <div class="dsp-chat-suggestions" id="dsp-chat-suggestions">
                        ${this.config.suggestions.map(s => `<button class="dsp-suggestion-btn">${s}</button>`).join('')}
                    </div>

                    <div class="dsp-chatbot-input">
                        <input type="text" id="dsp-chatbot-input" placeholder="${this.config.placeholder}" autocomplete="off">
                        <button class="dsp-send-btn" id="dsp-chatbot-send">
                            <svg viewBox="0 0 24 24">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                            </svg>
                        </button>
                    </div>

                    <div class="dsp-chatbot-powered">Powered by Dispusipda Pekanbaru</div>
                </div>
            `;

            document.body.appendChild(container);

            // Store element references
            this.elements = {
                toggle: document.getElementById('dsp-chatbot-toggle'),
                window: document.getElementById('dsp-chatbot-window'),
                greeting: document.getElementById('dsp-chatbot-greeting'),
                messages: document.getElementById('dsp-chatbot-messages'),
                input: document.getElementById('dsp-chatbot-input'),
                sendBtn: document.getElementById('dsp-chatbot-send'),
                suggestions: document.getElementById('dsp-chat-suggestions')
            };
        }

        attachEventListeners() {
            this.elements.toggle.addEventListener('click', () => this.toggleChat());
            this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
            this.elements.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
            this.elements.suggestions.addEventListener('click', (e) => {
                if (e.target.classList.contains('dsp-suggestion-btn')) {
                    this.elements.input.value = e.target.textContent;
                    this.sendMessage();
                }
            });
            this.elements.greeting.querySelector('.dsp-close-greeting').addEventListener('click', () => {
                this.elements.greeting.classList.remove('show');
            });
        }

        initSession() {
            let sessionId = localStorage.getItem('dsp_chatbot_session');
            if (!sessionId) {
                sessionId = this.generateUUID();
                localStorage.setItem('dsp_chatbot_session', sessionId);
            }
            this.state.sessionId = sessionId;
        }

        generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
                const r = Math.random() * 16 | 0;
                return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
        }

        toggleChat() {
            this.state.isOpen = !this.state.isOpen;
            this.elements.window.classList.toggle('open', this.state.isOpen);
            this.elements.toggle.classList.toggle('active', this.state.isOpen);
            this.elements.greeting.classList.remove('show');

            if (this.state.isOpen) {
                this.elements.input.focus();
                if (this.elements.messages.children.length === 0) {
                    this.addBotMessage(this.config.greetingMessage);
                }
            }
        }

        showGreetingAfterDelay() {
            setTimeout(() => {
                if (!this.state.isOpen && !this.state.greetingShown) {
                    this.elements.greeting.classList.add('show');
                    this.state.greetingShown = true;

                    setTimeout(() => {
                        if (!this.state.isOpen) {
                            this.elements.greeting.classList.remove('show');
                        }
                    }, this.config.greetingAutoCloseDelay);
                }
            }, 2000);
        }

        addMessage(content, isUser = false) {
            const div = document.createElement('div');
            div.className = `dsp-chat-message ${isUser ? 'user' : 'bot'}`;

            const avatarSvg = isUser
                ? '<svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'
                : '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>';

            div.innerHTML = `
                <div class="dsp-chat-avatar">${avatarSvg}</div>
                <div class="dsp-chat-bubble">${this.escapeHtml(content)}</div>
            `;

            this.elements.messages.appendChild(div);
            this.scrollToBottom();
        }

        addBotMessage(content) {
            this.addMessage(content, false);
        }

        addUserMessage(content) {
            this.addMessage(content, true);
        }

        showTyping() {
            const div = document.createElement('div');
            div.className = 'dsp-chat-message bot';
            div.id = 'dsp-typing';
            div.innerHTML = `
                <div class="dsp-chat-avatar">
                    <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>
                </div>
                <div class="dsp-chat-bubble">
                    <div class="dsp-typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            `;
            this.elements.messages.appendChild(div);
            this.scrollToBottom();
            this.state.isTyping = true;
        }

        hideTyping() {
            const typing = document.getElementById('dsp-typing');
            if (typing) typing.remove();
            this.state.isTyping = false;
        }

        scrollToBottom() {
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        async sendMessage() {
            const message = this.elements.input.value.trim();
            if (!message || this.state.isTyping) return;

            this.addUserMessage(message);
            this.elements.input.value = '';
            this.elements.suggestions.style.display = 'none';
            this.showTyping();

            try {
                const response = await fetch(`${this.config.apiUrl}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        session_id: this.state.sessionId
                    })
                });

                const data = await response.json();
                this.hideTyping();

                if (data.error) {
                    this.addBotMessage('Maaf, terjadi kesalahan. Silakan coba lagi.');
                } else {
                    if (data.session_id) {
                        this.state.sessionId = data.session_id;
                        localStorage.setItem('dsp_chatbot_session', data.session_id);
                    }
                    this.addBotMessage(data.response);
                }
            } catch (error) {
                console.error('Chatbot Error:', error);
                this.hideTyping();
                this.addBotMessage('Maaf, tidak dapat terhubung ke server. Silakan coba lagi nanti.');
            }
        }

        darkenColor(color, percent) {
            const num = parseInt(color.replace('#', ''), 16);
            const amt = Math.round(2.55 * percent);
            const R = Math.max((num >> 16) - amt, 0);
            const G = Math.max((num >> 8 & 0x00FF) - amt, 0);
            const B = Math.max((num & 0x0000FF) - amt, 0);
            return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
        }

        lightenColor(color, percent) {
            const num = parseInt(color.replace('#', ''), 16);
            const amt = Math.round(2.55 * percent);
            const R = Math.min((num >> 16) + amt, 255);
            const G = Math.min((num >> 8 & 0x00FF) + amt, 255);
            const B = Math.min((num & 0x0000FF) + amt, 255);
            return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
        }
    }

    // ==================== EXPORT ====================
    window.ChatbotWidget = {
        init: function(config) {
            return new ChatbotWidget(config);
        }
    };
})();
