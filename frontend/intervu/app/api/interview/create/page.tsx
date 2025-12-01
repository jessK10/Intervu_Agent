"use client";

import { useState } from "react";

export default function CreateInterviewPage() {
  const [role, setRole] = useState("");
  const [level, setLevel] = useState("");
  const [type, setType] = useState(""); 
  const [techstack, setTechstack] = useState("");
  const [amount, setAmount] = useState(5);
  const [questions, setQuestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setQuestions([]);

    try {
      const res = await fetch("/api/vapi/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role,
          level,
          type,
          techstack,
          amount,
          userid: "demo-user-123",
        }),
      });

      const data = await res.json();
      if (res.ok && data.success) {
        setQuestions(data.questions || []); // ✅ fixed
      } else {
        alert(data.error || "Failed to generate questions");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-6">
      <h1 className="text-2xl font-bold mb-6">Create Interview</h1>

      <div className="space-y-4 w-full max-w-md">
        <input
          type="text"
          placeholder="Role (e.g. Frontend Developer)"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="w-full px-4 py-2 rounded bg-gray-800 text-white"
        />
        <input
          type="text"
          placeholder="Level (e.g. Junior, Mid, Senior)"
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="w-full px-4 py-2 rounded bg-gray-800 text-white"
        />
        <input
          type="text"
          placeholder="Type (Technical / Behavioural / Mixed)"
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="w-full px-4 py-2 rounded bg-gray-800 text-white"
        />
        <input
          type="text"
          placeholder="Tech stack (comma separated, e.g. React, Node.js)"
          value={techstack}
          onChange={(e) => setTechstack(e.target.value)}
          className="w-full px-4 py-2 rounded bg-gray-800 text-white"
        />
        <input
          type="number"
          placeholder="Number of questions"
          value={amount}
          onChange={(e) => setAmount(Number(e.target.value))}
          className="w-full px-4 py-2 rounded bg-gray-800 text-white"
          min={1}
          max={20}
        />

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-purple-600 hover:bg-purple-700 py-2 rounded"
        >
          {loading ? "Generating..." : "Generate Interview"}
        </button>
      </div>

      <div className="mt-8 w-full max-w-xl">
        {questions.length > 0 && (
          <ul className="space-y-3">
            {questions.map((q, i) => (
              <li key={i} className="bg-gray-800 p-4 rounded">
                {q}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
