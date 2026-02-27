import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
    const [isRegister, setIsRegister] = useState(false);
    const [form, setForm] = useState({
        email: "",
        username: "",
        password: "",
        confirmPassword: "",
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const { login, register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) =>
        setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        if (isRegister && form.password !== form.confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        setLoading(true);
        try {
            if (isRegister) {
                await register({
                    username: form.username,
                    email: form.email,
                    password: form.password,
                });
            } else {
                await login(form.email, form.password);
            }
            navigate("/chat");
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (typeof detail === "string") setError(detail);
            else if (detail?.message) setError(detail.message);
            else setError("Something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-card">
                <div className="login-header">
                    <div className="login-logo">💬</div>
                    <h1>ChatSphere</h1>
                    <p>{isRegister ? "Create your account" : "Welcome back"}</p>
                </div>

                {error && <div className="login-error">{error}</div>}

                <form onSubmit={handleSubmit} className="login-form">
                    {isRegister && (
                        <div className="form-group">
                            <label htmlFor="username">Username</label>
                            <input
                                id="username"
                                name="username"
                                value={form.username}
                                onChange={handleChange}
                                placeholder="john_doe"
                                required
                            />
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            value={form.email}
                            onChange={handleChange}
                            placeholder="you@example.com"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            value={form.password}
                            onChange={handleChange}
                            placeholder="••••••••"
                            required
                            minLength={8}
                        />
                    </div>

                    {isRegister && (
                        <div className="form-group">
                            <label htmlFor="confirmPassword">Confirm Password</label>
                            <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                value={form.confirmPassword}
                                onChange={handleChange}
                                placeholder="••••••••"
                                required
                                minLength={8}
                            />
                        </div>
                    )}

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? "Please wait…" : isRegister ? "Register" : "Login"}
                    </button>
                </form>

                <p className="login-toggle">
                    {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
                    <button
                        type="button"
                        className="btn-link"
                        onClick={() => {
                            setIsRegister(!isRegister);
                            setError("");
                        }}
                    >
                        {isRegister ? "Login" : "Register"}
                    </button>
                </p>
            </div>
        </div>
    );
}
