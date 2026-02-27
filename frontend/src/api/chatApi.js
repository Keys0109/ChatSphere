import api from "./axios";


export const authApi = {
    register: (data) => api.post("/auth/register", data),
    login: (data) => api.post("/auth/login", data),
    refresh: (refreshToken) =>
        api.post("/auth/refresh", { refresh_token: refreshToken }),
    getMe: () => api.get("/auth/me"),
};


export const userApi = {
    getProfile: () => api.get("/users/me"),
    updateProfile: (data) => api.put("/users/me", data),
    searchUsers: (query) => api.get(`/users/search?q=${encodeURIComponent(query)}`),
    getUserById: (userId) => api.get(`/users/${userId}`),
};


export const chatApi = {
    getChats: () => api.get("/chats/"),
    createChat: (data) => api.post("/chats/", data),
    getChatById: (chatId) => api.get(`/chats/${chatId}`),
    deleteChat: (chatId) => api.delete(`/chats/${chatId}`),
    addParticipant: (chatId, userId) =>
        api.post(`/chats/${chatId}/participants`, { user_id: userId }),
};


export const messageApi = {
    getMessages: (chatId, params = {}) =>
        api.get(`/messages/${chatId}`, { params }),
    sendMessage: (chatId, data) => api.post(`/messages/${chatId}`, data),
    editMessage: (messageId, content) =>
        api.put(`/messages/${messageId}`, { content }),
    deleteMessage: (messageId) => api.delete(`/messages/${messageId}`),
    markAsRead: (chatId) => api.post(`/messages/${chatId}/read`),
};
