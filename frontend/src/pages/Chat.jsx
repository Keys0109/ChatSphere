import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import { chatApi, messageApi } from "../api/chatApi";
import { connectSocket, disconnectSocket, getSocket } from "../socket/socket";
import { getAccessToken } from "../utils/token";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";

export default function Chat() {
    const { user } = useAuth();
    const [chats, setChats] = useState([]);
    const [selectedChat, setSelectedChat] = useState(null);
    const [messages, setMessages] = useState([]);
    const [loadingChats, setLoadingChats] = useState(true);


    const fetchChats = useCallback(async () => {
        try {
            const res = await chatApi.getChats();
            setChats(res.data.chats || []);
        } catch (err) {
            console.error("Failed to load chats:", err);
        } finally {
            setLoadingChats(false);
        }
    }, []);


    const fetchMessages = useCallback(async (chatId) => {
        try {
            const res = await messageApi.getMessages(chatId);
            setMessages(res.data.messages || []);
        } catch (err) {
            console.error("Failed to load messages:", err);
        }
    }, []);


    useEffect(() => {
        const token = getAccessToken();
        if (token) connectSocket(token);
        fetchChats();

        return () => disconnectSocket();
    }, [fetchChats]);


    useEffect(() => {
        const socket = getSocket();
        if (!socket) return;

        const handleNewMessage = (msg) => {

            if (selectedChat && msg.chat_id === selectedChat._id) {
                setMessages((prev) => [...prev, msg]);
            }

            setChats((prev) =>
                prev.map((c) =>
                    c._id === msg.chat_id
                        ? {
                            ...c,
                            last_message_preview: msg.content?.slice(0, 60),
                            last_message_at: msg.created_at,
                        }
                        : c
                )
            );
        };

        socket.on("new_message", handleNewMessage);
        return () => socket.off("new_message", handleNewMessage);
    }, [selectedChat]);


    useEffect(() => {
        const socket = getSocket();
        if (!socket || !selectedChat) return;

        socket.emit("join_chat", { chat_id: selectedChat._id });
        fetchMessages(selectedChat._id);

        return () => {
            socket.emit("leave_chat", { chat_id: selectedChat._id });
        };
    }, [selectedChat, fetchMessages]);

    const handleSelectChat = (chat) => {
        setSelectedChat(chat);
        setMessages([]);
    };

    const handleChatCreated = (newChat) => {
        setChats((prev) => [newChat, ...prev]);
        setSelectedChat(newChat);
    };

    return (
        <div className="chat-page">
            <Sidebar
                chats={chats}
                selectedChat={selectedChat}
                onSelectChat={handleSelectChat}
                onChatCreated={handleChatCreated}
                loading={loadingChats}
            />
            <ChatWindow
                chat={selectedChat}
                messages={messages}
                currentUser={user}
            />
        </div>
    );
}
