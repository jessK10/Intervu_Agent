"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Avatar from "@/components/Avatar";
import { Button } from "@/components/ui/button";

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

type User = {
  id: string;
  name: string;
  email: string;
  role: string;
};

enum CallStatus {
  Inactive = "inactive",
  Active = "active",
  Finished = "finished",
}

const synth = typeof window !== "undefined" ? window.speechSynthesis : null;
const SpeechRecognition =
  typeof window !== "undefined"
    ? (window.SpeechRecognition || (window as any).webkitSpeechRecognition)
    : null;

export default function InterviewStartPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [callStatus, setCallStatus] = useState<CallStatus>(CallStatus.Inactive);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const [questions, setQuestions] = useState<string[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [listening, setListening] = useState(false);

  // 🎯 Interview setup form states
  const [role, setRole] = useState("Frontend Developer");
  const [level, setLevel] = useState("Junior");
  const [techstack, setTechstack] = useState("React, Next.js");
  const [amount, setAmount] = useState(3);
  const [type, setType] = useState("Technical");

  // ✅ Protect page + fetch user
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.replace("/login?next=/interview/start");
      return;
    }

    (async () => {
      try {
        const res = await fetch("http://localhost:8000/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Not authenticated");
        const data: User = await res.json();
        setUser(data);
      } catch (err) {
        console.error("Auth error:", err);
        localStorage.removeItem("token");
        router.replace("/login?next=/interview/start");
      }
    })();
  }, [router]);

  // 🔹 Speak helper
  const speak = (text: string, onEnd?: () => void) => {
    if (synth) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => {
        setIsSpeaking(false);
        if (onEnd) onEnd();
      };
      synth.speak(utterance);
    }
  };

  // 🔹 Listen for voice answers
  const startListening = () => {
    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setAnswers((prev) => {
        const updated = [...prev];
        updated[currentQuestionIndex] = transcript;
        return updated;
      });

      // 👉 Move to next question OR end interview
      if (currentQuestionIndex + 1 < questions.length) {
        setCurrentQuestionIndex((prev) => prev + 1);
      } else {
        endCall(); // ✅ Auto end when last question answered
      }
    };

    recognition.start();
  };

  // 🔹 Auto-speak new question when index changes
  useEffect(() => {
    if (
      callStatus === CallStatus.Active &&
      questions.length > 0 &&
      currentQuestionIndex < questions.length
    ) {
      speak(questions[currentQuestionIndex], () => {
        startListening();
      });
    }
  }, [currentQuestionIndex, questions, callStatus]);

  // ✅ Start interview
  const startCall = async () => {
    setCallStatus(CallStatus.Active);

    try {
      const qres = await fetch("/api/vapi/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role,
          level,
          type,
          techstack,
          amount,
          userid: user?.id || "guest",
        }),
      });

      const qdata = await qres.json();
      if (qres.ok) {
        setQuestions(qdata.questions || []);
        setCurrentQuestionIndex(0);
      }
    } catch (err) {
      console.error("Failed to fetch questions:", err);
    }
  };

  // ✅ End call + save answers
const endCall = async () => {
  setCallStatus(CallStatus.Finished);

  try {
    const token = localStorage.getItem("token");
    await fetch("http://localhost:8000/interview/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        user_id: user?.id,
        questions,
        answers,
        role,       // <-- include role
        level,      // <-- include level
        type,       // <-- include type
        techstack: techstack.split(",").map((t) => t.trim()), // array
        created_at: new Date().toISOString(),
      }),
    });
    console.log("✅ Interview saved");
  } catch (err) {
    console.error("❌ Failed to save interview:", err);
  }

  // ✅ Redirect after 5 seconds
  setTimeout(() => {
    router.push("/dashboard");
  }, 5000);
};


  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center px-6 py-12">
      <h2 className="text-2xl font-bold mb-10">Interview Session</h2>

      {/* AI + Candidate cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10 w-full max-w-4xl">
        {/* AI Interviewer */}
        <div className="flex flex-col items-center justify-center bg-gradient-to-b from-indigo-900 to-indigo-950 rounded-2xl shadow-lg p-10 border border-gray-700 relative">
          <div className="relative">
            {isSpeaking && (
              <span className="absolute inset-0 rounded-full bg-purple-500 opacity-75 animate-ping"></span>
            )}
            <Image
              src="/logo.svg"
              alt="AI Interviewer"
              width={100}
              height={100}
              className="mb-4 relative z-10"
            />
          </div>
          <h3 className="text-xl font-semibold">AI Interviewer</h3>
        </div>

        {/* Candidate */}
        <div className="flex flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-gray-950 rounded-2xl shadow-lg p-10 border border-gray-700">
          {user && (
            <>
              <Avatar email={user.email} name={user.name} size={80} />
              <h3 className="text-xl font-semibold mt-4">{user.name}</h3>
            </>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="mt-12 text-center w-full max-w-md">
        {callStatus === CallStatus.Inactive && (
          <div className="space-y-4 text-left bg-gray-900 p-6 rounded-xl border border-gray-700">
            {/* Form */}
            <div>
              <label className="block text-sm text-gray-300">Role</label>
              <input
                type="text"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-300">Level</label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white"
              >
                <option>Junior</option>
                <option>Mid</option>
                <option>Senior</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-300">Tech Stack</label>
              <input
                type="text"
                value={techstack}
                onChange={(e) => setTechstack(e.target.value)}
                className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-300">
                Number of Questions
              </label>
              <input
                type="number"
                min={1}
                max={10}
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-300">Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white"
              >
                <option>Technical</option>
                <option>Behavioral</option>
                <option>Mixed</option>
              </select>
            </div>

            <Button
              onClick={startCall}
              className="w-full px-10 py-2 rounded-full bg-green-600 hover:bg-green-700 mt-4"
            >
              Start Interview
            </Button>
          </div>
        )}

        {callStatus === CallStatus.Active && (
          <>
            {questions.length > 0 ? (
              currentQuestionIndex < questions.length ? (
                <h3 className="text-xl mb-4">
                  Q{currentQuestionIndex + 1}: {questions[currentQuestionIndex]}
                </h3>
              ) : (
                <h3 className="text-xl font-bold">Interview Finished 🎉</h3>
              )
            ) : (
              <p className="text-gray-400">Loading questions...</p>
            )}

            <Button
              onClick={endCall}
              className="mt-6 px-10 py-2 rounded-full bg-red-600 hover:bg-red-700"
            >
              End Call
            </Button>
          </>
        )}

        {callStatus === CallStatus.Finished && (
          <p className="mt-6 text-sm text-gray-400">
            Saving interview... Redirecting you to dashboard in 5s...
          </p>
        )}
      </div>
    </div>
  );
}
