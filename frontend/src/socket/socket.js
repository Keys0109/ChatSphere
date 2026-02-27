import { io } from "socket.io-client";

const SOCKET_URL = "http://localhost:8000";

let socket = null;

export const connectSocket = (token) => {
    if (socket) return socket;

    socket = io(SOCKET_URL, {
        path: "/socket.io/",
        auth: { token },
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 2000,
    });

    socket.on("connect", () => {
        console.log("[Socket] Connected:", socket.id);
    });

    socket.on("connect_error", (err) => {
        console.error("[Socket] Connection error:", err.message);
    });

    socket.on("disconnect", (reason) => {
        console.log("[Socket] Disconnected:", reason);
    });

    return socket;
};

export const getSocket = () => socket;

export const disconnectSocket = () => {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
};
