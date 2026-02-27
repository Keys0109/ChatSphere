import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { userApi, chatApi } from "../api/chatApi";

export default function Sidebar({
    chats,
    selectedChat,
    onSelectChat,
    onChatCreated,
    loading,
}) {
    const { user, logout } = useAuth();
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const [searching, setSearching] = useState(false);

    const handleSearch = async (e) => {
        const q = e.target.value;
        setSearchQuery(q);

        if (q.length < 2) {
            setSearchResults([]);
            return;
        }

        setSearching(true);
        try {
            const res = await userApi.searchUsers(q);
            setSearchResults(res.data.users || []);
        } catch {
            setSearchResults([]);
        } finally {
            setSearching(false);
        }
    };

    const startChat = async (targetUserId) => {
        try {
            const res = await chatApi.createChat({
                chat_type: "direct",
                participant_ids: [targetUserId],
            });
            onChatCreated(res.data);
            setSearchQuery("");
            setSearchResults([]);
        } catch (err) {
            console.error("Failed to create chat:", err);
        }
    };

    const formatTime = (dateStr) => {
        if (!dateStr) return "";
        const d = new Date(dateStr);
        const now = new Date();
        if (d.toDateString() === now.toDateString()) {
            return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        }
        return d.toLocaleDateString([], { month: "short", day: "numeric" });
    };

    return (
        <aside className="sidebar">
            {}
            <div className="sidebar-header">
                <div className="sidebar-user">
                    <div className="avatar">{user?.username?.[0]?.toUpperCase() || "?"}</div>
                    <span className="sidebar-username">{user?.username}</span>
                </div>
                <button className="btn-icon" onClick={logout} title="Logout">
                    ⏻
                </button>
            </div>

            {}
            <div className="sidebar-search">
                <input
                    type="text"
                    placeholder="Search users…"
                    value={searchQuery}
                    onChange={handleSearch}
                />
            </div>

            {}
            {searchQuery.length >= 2 && (
                <div className="search-results">
                    {searching && <div className="search-loading">Searching…</div>}
                    {!searching && searchResults.length === 0 && (
                        <div className="search-empty">No users found</div>
                    )}
                    {searchResults.map((u) => (
                        <div
                            key={u._id}
                            className="search-result-item"
                            onClick={() => startChat(u._id)}
                        >
                            <div className="avatar avatar-sm">
                                {u.username?.[0]?.toUpperCase()}
                            </div>
                            <span>{u.username}</span>
                            {u.is_online && <span className="online-dot" />}
                        </div>
                    ))}
                </div>
            )}

            {}
            <div className="chat-list">
                {loading && <div className="chat-list-loading">Loading chats…</div>}
                {!loading && chats.length === 0 && (
                    <div className="chat-list-empty">
                        No chats yet. Search for a user to start chatting!
                    </div>
                )}
                {chats.map((chat) => (
                    <div
                        key={chat._id}
                        className={`chat-item ${selectedChat?._id === chat._id ? "active" : ""
                            }`}
                        onClick={() => onSelectChat(chat)}
                    >
                        <div className="avatar">
                            {(chat.name || "C")[0].toUpperCase()}
                        </div>
                        <div className="chat-item-info">
                            <div className="chat-item-top">
                                <span className="chat-item-name">
                                    {chat.name || "Direct Chat"}
                                </span>
                                <span className="chat-item-time">
                                    {formatTime(chat.last_message_at)}
                                </span>
                            </div>
                            <p className="chat-item-preview">
                                {chat.last_message_preview || "No messages yet"}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </aside>
    );
}
