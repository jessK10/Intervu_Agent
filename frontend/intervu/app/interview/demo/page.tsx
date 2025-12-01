"use client";

import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

const demoData: Record<string, any> = {
  demo1: {
    title: "Behavioral Interview",
    questions: [
      "Tell me about a time you resolved a conflict in a team.",
      "Describe a challenge you faced and how you handled it.",
    ],
    answers: ["Demo answer 1", "Demo answer 2"],
  },
  demo2: {
    title: "Data Science Interview",
    questions: [
      "What is overfitting in machine learning?",
      "Explain the difference between supervised and unsupervised learning.",
    ],
    answers: ["Demo answer 1", "Demo answer 2"],
  },
  demo3: {
    title: "Mobile App Developer Interview",
    questions: [
      "Explain the difference between React Native and native development.",
      "What are common performance issues in mobile apps?",
    ],
    answers: ["Demo answer 1", "Demo answer 2"],
  },
};

export default function DemoInterviewPage() {
  const { id } = useParams();
  const router = useRouter();
  const interview = demoData[id as string];

  if (!interview) {
    return <p className="text-gray-400 p-10">Demo interview not found</p>;
  }

  return (
    <div className="min-h-screen bg-black text-white p-10 space-y-6">
      <h2 className="text-3xl font-bold">{interview.title}</h2>

      <ul className="space-y-4">
        {interview.questions.map((q: string, i: number) => (
          <li
            key={i}
            className="bg-gray-900 p-4 rounded-lg border border-gray-700"
          >
            <p>
              <strong>Q{i + 1}:</strong> {q}
            </p>
            <p>
              <strong>A:</strong> {interview.answers[i]}
            </p>
          </li>
        ))}
      </ul>

      {/* Back button */}
      <Button
        className="bg-purple-600 hover:bg-purple-700 rounded-xl px-6 py-2"
        onClick={() => router.push("/dashboard")}
      >
        ← Back to Dashboard
      </Button>
    </div>
  );
}
