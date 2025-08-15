import React, { useEffect, useState } from "react";
import { getPosts } from "../api";
import type {Post} from "../types";

interface Props {
    token: string;
}

export const PostList: React.FC<Props> = ({ token }) => {
    const [posts, setPosts] = useState<Post[]>([]);

    useEffect(() => {
        const fetchPosts = async () => {
            const data = await getPosts(token);
            setPosts(data);
        };
        fetchPosts();
    }, [token]);

    return (
        <div>
            {posts.map((post) => (
                <div key={post.id}>
                    <h2>{post.title}</h2>
                    <div dangerouslySetInnerHTML={{ __html: post.content }} />
                    {post.imageUrl && <img src={post.imageUrl} alt="" />}
                    {post.videoUrl && <video src={post.videoUrl} controls />}
                </div>
            ))}
        </div>
    );
};
