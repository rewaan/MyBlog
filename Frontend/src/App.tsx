import React, { useState } from "react";
import { LoginForm } from "./components/LoginForm";
import { PostList } from "./components/PostList";

const App: React.FC = () => {
    const [token, setToken] = useState<string>("");

    return (
        <div>
            {!token ? (
                <LoginForm setToken={setToken} />
            ) : (
                <PostList token={token} />
            )}
        </div>
    );
};

export default App;
