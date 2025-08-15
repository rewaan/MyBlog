import React, { useState } from "react";
import { login } from "../api";
import type {LoginRequest} from "../types";

interface Props {
    setToken: (token: string) => void;
}

export const LoginForm: React.FC<Props> = ({ setToken }) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const data: LoginRequest = { username, password };
            const result = await login(data);
            setToken(result.access_token);
        } catch (err: any) {
            setError("Nieprawidłowe dane");
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Zaloguj</button>
            {error && <p>{error}</p>}
        </form>
    );
};
