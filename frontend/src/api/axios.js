import axios from "axios";
import { getAccessToken, removeTokens } from "../utils/token";

const API_BASE_URL = "http://localhost:8000/api/v1";

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: { "Content-Type": "application/json" },
});


api.interceptors.request.use(
    (config) => {
        const token = getAccessToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);


api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            removeTokens();
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

export default api;
