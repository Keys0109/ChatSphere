import { useState, useRef, useEffect } from "react";
import { getSocket } from "../socket/socket";
import { messageApi } from "../api/chatApi";
import Message from "./Message";

export default function ChatWindow({ chat, messages, currentUser }) {
    const [input, setInput] = useState("");
    const [typingUsers, setTypingUsers] = useState([]);
    const [sending, setSending] = useState(false);
    const messagesEndRef = useRef(null);
    const typingTimeoutRef = useRef(null);


    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);


    useEffect(() => {
        const socket = getSocket();
        if (!socket || !chat) return;

        const handleTyping = (data) => {
            if (data.chat_id !== chat._id) return;
            if (data.user_id === currentUser?._id) return;

            setTypingUsers((prev) => {
                if (data.is_typing) {
                    return prev.includes(data.user_id) ? prev : [...prev, data.user_id];
                }
                return prev.filter((id) => id !== data.user_id);
            });
        };

        socket.on("user_typing", handleTyping);
        return () => socket.off("user_typing", handleTyping);
    }, [chat, currentUser]);


    useEffect(() => {
        setTypingUsers([]);
    }, [chat]);

    const handleTyping = () => {
        const socket = getSocket();
        if (!socket || !chat) return;

        socket.emit("typing_start", { chat_id: chat._id });

        if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
        typingTimeoutRef.current = setTimeout(() => {
            socket.emit("typing_stop", { chat_id: chat._id });
        }, 2000);
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || !chat || sending) return;

        setSending(true);
        try {
            await messageApi.sendMessage(chat._id, { content: input.trim() });
            setInput("");

            const socket = getSocket();
            if (socket) socket.emit("typing_stop", { chat_id: chat._id });
        } catch (err) {
            console.error("Failed to send message:", err);
        } finally {
            setSending(false);
        }
    };

    if (!chat) {
        return (
            <main className="chat-window chat-window--empty">
                <div className="empty-state">
                    <span className="empty-icon">💬</span>
                    <h2>Welcome to ChatSphere</h2>
                    <p>Select a chat or search for a user to start messaging</p>
                </div>
            </main>
        );
    }

    return (
        <main className="chat-window">
            {}
            <div className="chat-header">
                <div className="avatar">
                    {(chat.name || "C")[0].toUpperCase()}
                </div>
                <div className="chat-header-info">
                    <h3>{chat.name || "Direct Chat"}</h3>
                    <span className="chat-header-sub">
                        {chat.chat_type === "group"
                            ? `${chat.participants?.length || 0} members`
                            : "Direct message"}
                    </span>
                </div>
            </div>

            {}
            <div className="messages-container">
                {messages.length === 0 && (
                    <div className="messages-empty">
                        No messages yet. Say hello! 👋
                    </div>
                )}
                {messages.map((msg) => (
                    <Message
                        key={msg._id}
                        message={msg}
                        isOwn={msg.sender_id === currentUser?._id}
                    />
                ))}
                <div ref={messagesEndRef} />
            </div>

            {}
            {typingUsers.length > 0 && (
                <div className="typing-indicator">
                    <span className="typing-dots">
                        <span /><span /><span />
                    </span>
                    Someone is typing…
                </div>
            )}

            {}
            <form className="message-input" onSubmit={handleSend}>
                <input
                    type="text"
                    placeholder="Type a message…"
                    value={input}
                    onChange={(e) => {
                        setInput(e.target.value);
                        handleTyping();
                    }}
                />
                <button type="submit" className="btn-send" disabled={!input.trim() || sending}>
                    ➤
                </button>
            </form>
        </main>
    );
}
