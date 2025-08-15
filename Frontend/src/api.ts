import axios from "axios";
import type {LoginRequest, TokenResponse, Post} from "./types";

const API_URL = "https://twoj-backend.up.railway.app"; // dostosuj do Railway

export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true, // żeby refresh token httpOnly działał
});

// Login
export const login = async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>("/login", data);
    return response.data;
};

// Refresh token
export const refreshToken = async (): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>("/refresh");
    return response.data;
};

// Pobranie postów (przykład)
export const getPosts = async (token: string): Promise<Post[]> => {
    const response = await api.get<Post[]>("/posts", {
        headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
};
