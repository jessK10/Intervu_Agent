"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { getToken, logout } from "@/lib/auth";

type User = {
  id: string;
  name: string;
  email: string;
  role: string;
};

type Interview = {
  id?: string;
  _id?: string;
  questions?: string[];
  answers?: string[];
  role?: string;
  level?: string;
  type?: string;
  techstack?: string[];
  created_at?: string;
  score?: string;
  logo?: string;
  description?: string;
};

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [pastInterviews, setPastInterviews] = useState<Interview[]>([]);

  // ✅ Load logged-in user
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }

    (async () => {
      try {
        const res = await fetch("http://localhost:8000/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          logout();
          setUser(null);
          return;
        }

        const data: User = await res.json();
        setUser(data);
      } catch {
        logout();
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // ✅ Load Past Interviews from backend
  useEffect(() => {
    const token = getToken();
    if (!token) return;

    (async () => {
      try {
        const res = await fetch("http://localhost:8000/interview/history", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setPastInterviews(data || []);
        }
      } catch (err) {
        console.error("Failed to load past interviews:", err);
      }
    })();
  }, []);

  const handleStartInterview = () => {
    if (user) router.push("/interview/start");
    else router.push("/login?next=/interview/start");
  };

  // Demo Interviews
  const availableInterviews: Interview[] = [
    {
      id: "demo1",
      role: "Behavioral Interview",
      type: "Non-Technical",
      description:
        "Behavioral round to test communication, leadership, and problem solving.",
      logo: "/icons/redis.svg",
      created_at: "2024-03-12T00:00:00Z",
    },
    {
      id: "demo2",
      role: "Data Science Interview",
      type: "Technical",
      description:
        "Challenge yourself with ML, Python, and data analysis questions.",
      logo: "/icons/aws.svg",
      techstack: ["Python", "Pandas", "NumPy"],
      created_at: "2024-03-20T00:00:00Z",
    },
    {
      id: "demo3",
      role: "Mobile App Developer Interview",
      type: "Technical",
      description:
        "Covers iOS and Android app development with React Native and Swift.",
      logo: "/icons/react.svg",
      techstack: ["React Native", "Swift", "Android"],
      created_at: "2024-03-22T00:00:00Z",
    },
  ];

  return (
    <div className="min-h-screen bg-black text-white px-8 py-12 space-y-16">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-purple-900 to-indigo-900 rounded-2xl p-10 flex items-center justify-between shadow-xl overflow-hidden">
        <div className="max-w-xl space-y-4 relative z-10">
          <h2 className="text-3xl font-bold leading-snug">
            Get Interview-Ready with AI-Powered Practice & Feedback
          </h2>
          <p className="text-gray-300">
            Practice real interview questions & get instant feedback.
          </p>
          <Button
            className="bg-purple-600 hover:bg-purple-700 rounded-xl px-6 py-2"
            onClick={handleStartInterview}
          >
            Start an Interview
          </Button>
        </div>

        <div className="hidden md:block relative z-10">
          <div className="absolute -inset-20 rounded-full bg-purple-500/30 blur-3xl animate-pulse"></div>
          <Image
            src="/robot.png"
            alt="Interview Bot"
            width={420}
            height={420}
            className="drop-shadow-2xl animate-float relative z-10"
          />
        </div>
      </div>

      {/* Past Interviews */}
      <section>
        <h2 className="text-2xl font-semibold mb-6">Your Past Interviews</h2>
        {loading ? (
          <p className="text-gray-400">Loading...</p>
        ) : pastInterviews.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {pastInterviews.map((interview, index) => (
              <InterviewCard
                key={interview.id || interview._id || index}
                interview={interview}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-400">No past interviews yet. Start one now!</p>
        )}
      </section>

      {/* Demo / Available Interviews */}
      <section>
        <h2 className="text-2xl font-semibold mb-6">Available Interviews</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {availableInterviews.map((interview) => (
            <InterviewCard key={interview.id} interview={interview} />
          ))}
        </div>
      </section>
    </div>
  );
}

// ✅ Reusable Interview Card
function InterviewCard({ interview }: { interview: Interview }) {
  const router = useRouter();

  const handleViewInterview = () => {
    const id = interview.id || interview._id;
    if (!id) return;

    if (typeof id === "string" && id.startsWith("demo")) {
      router.push(`/interview/demo/${id}`);
    } else {
      router.push(`/interview/${id}`);
    }
  };

  const date = interview.created_at
    ? new Date(interview.created_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "N/A";

  return (
    <Card className="relative bg-gradient-to-b from-gray-900 to-gray-800 border border-gray-700 rounded-2xl shadow-lg hover:scale-[1.02] transition-transform duration-300">
      {/* Badge */}
      <span className="absolute top-3 right-3 text-xs px-3 py-1 bg-purple-600/30 text-purple-300 rounded-md font-medium">
        {interview.type || "Custom"}
      </span>

      <CardHeader className="flex items-center gap-3">
        {interview.logo && (
          <Image
            src={interview.logo}
            alt="logo"
            width={45}
            height={44}
            className="rounded-full"
          />
        )}
        <div>
          <CardTitle className="text-lg text-white">
            {interview.role || "Interview"}
          </CardTitle>
          <p className="text-xs text-gray-400">{date}</p>
          {interview.level && (
            <p className="text-xs text-gray-400">Level: {interview.level}</p>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-3 text-gray-300">
        {interview.description ? (
          <p className="text-sm line-clamp-3">{interview.description}</p>
        ) : (
          <p className="text-sm text-gray-500">
            {interview.questions?.length
              ? `${interview.questions.length} questions answered`
              : "No description"}
          </p>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between">
        {/* Tech tags */}
        <div className="flex flex-wrap gap-2 text-xs text-purple-300">
          {interview.techstack?.slice(0, 4).map((t, i) => (
            <span
              key={`${interview.id || interview._id}-${t}-${i}`}
              className="px-2 py-1 bg-purple-500/20 rounded-md border border-purple-500/30"
            >
              {t}
            </span>
          ))}
        </div>

        <Button
          className="bg-purple-600 hover:bg-purple-700 rounded-full px-5 py-1 text-sm"
          onClick={handleViewInterview}
        >
          View
        </Button>
      </CardFooter>
    </Card>
  );
}
