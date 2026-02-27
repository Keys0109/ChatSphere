export default function Message({ message, isOwn }) {
    const formatTime = (dateStr) => {
        if (!dateStr) return "";
        return new Date(dateStr).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    return (
        <div className={`message ${isOwn ? "message--own" : "message--other"}`}>
            <div className="message-bubble">
                {!isOwn && (
                    <span className="message-sender">{message.sender_id}</span>
                )}
                <p className="message-content">
                    {message.is_deleted ? (
                        <em className="message-deleted">This message was deleted</em>
                    ) : (
                        message.content
                    )}
                </p>
                <div className="message-meta">
                    <span className="message-time">{formatTime(message.created_at)}</span>
                    {message.is_edited && <span className="message-edited">edited</span>}
                </div>
            </div>
        </div>
    );
}
