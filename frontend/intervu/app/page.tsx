"use client";

import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>🚀 Welcome to InterVu</h1>
      <p>Your AI interview assistant is deployed successfully!</p>

      <button
        onClick={() => router.push("/dashboard")}
        style={{
          marginTop: "1rem",
          padding: "0.5rem 1rem",
          background: "purple",
          color: "white",
          borderRadius: "6px",
          border: "none",
          cursor: "pointer",
        }}
      >
        Go to Dashboard
      </button>
    </main>
  );
}
