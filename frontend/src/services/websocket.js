class WebSocketService {
    constructor() {
        this.ws = null;
        this.callbacks = new Set();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3秒
    }

    connect() {
        try {
            this.ws = new WebSocket('wss://www.100xlabs.top/ws');
            console.log('Creating WebSocket connection...');

            this.ws.onopen = () => {
                console.log('WebSocket connected successfully');
                this.reconnectAttempts = 0;
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('Received WebSocket message:', data);
                    this.callbacks.forEach(callback => {
                        console.log('Executing callback with data:', data);
                        callback(data);
                    });
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                    console.error('Raw message:', event.data);
                }
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                console.log('Attempting to reconnect...');
                this.reconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                console.error('WebSocket readyState:', this.ws.readyState);
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.reconnect();
        }
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => this.connect(), this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    subscribe(callback) {
        this.callbacks.add(callback);
    }

    unsubscribe(callback) {
        this.callbacks.delete(callback);
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

export const webSocketService = new WebSocketService(); 