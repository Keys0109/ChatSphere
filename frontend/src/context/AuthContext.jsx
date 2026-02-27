import { createContext, useContext, useState, useEffect } from "react";
import { authApi } from "../api/chatApi";
import {
    getAccessToken,
    setTokens,
    removeTokens,
} from "../utils/token";

const AuthContext = createContext(null);

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
    return ctx;
};

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);


    useEffect(() => {
        const hydrate = async () => {
            const token = getAccessToken();
            if (!token) {
                setLoading(false);
                return;
            }
            try {
                const res = await authApi.getMe();
                setUser(res.data);
            } catch {
                removeTokens();
            } finally {
                setLoading(false);
            }
        };
        hydrate();
    }, []);

    const login = async (email, password) => {
        const res = await authApi.login({ email, password });
        const { access_token, refresh_token, user: userData } = res.data;
        setTokens(access_token, refresh_token);
        setUser(userData);
        return userData;
    };

    const register = async ({ username, email, password }) => {
        const res = await authApi.register({ username, email, password });
        const { access_token, refresh_token, user: userData } = res.data;
        setTokens(access_token, refresh_token);
        setUser(userData);
        return userData;
    };

    const logout = () => {
        removeTokens();
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
}
