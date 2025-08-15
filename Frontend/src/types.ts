export interface Post {
    id: number;
    title: string;
    content: string;
    imageUrl?: string;
    videoUrl?: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: "bearer";
}
