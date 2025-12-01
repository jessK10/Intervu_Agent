"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function InterviewDetailPage() {
  const params = useParams();
  const router = useRouter();

  // handle id being string or string[]
  const interviewId = Array.isArray(params.id)
    ? params.id[0]
    : (params.id as string);

  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // helper to normalize backend shape → UI shape
  const normalizeInterview = (json: any) => {
    if (!json) return json;
    return {
      ...json,
      coaching_summary:
        json.coaching_summary ||
        json.feedback || // backend evaluation stores it here
        json.coaching?.summary_feedback ||
        "",
      coaching_tips:
        json.coaching_tips ||
        json.coaching?.tips ||
        [],
    };
  };

  // Load interview details
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      // no token -> go to login
      router.push(`/login?next=/interview/${interviewId}`);
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const res = await fetch(
          `http://localhost:8000/interview/${interviewId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (res.status === 401) {
          // token invalid/expired -> force login
          localStorage.removeItem("token");
          router.push(`/login?next=/interview/${interviewId}`);
          return;
        }

        if (!res.ok) {
          const msg = `Failed to load interview (${res.status})`;
          console.error(msg);
          setError(msg);
          return;
        }

        const json = await res.json();
        setData(normalizeInterview(json));
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Failed to load interview");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [interviewId, router]);

  // Call backend evaluation endpoint
  const handleEvaluate = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push(`/login?next=/interview/${interviewId}`);
      return;
    }

    try {
      setEvaluating(true);
      setError(null);

      const res = await fetch(
        `http://localhost:8000/interview/${interviewId}/evaluate`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.status === 401) {
        localStorage.removeItem("token");
        router.push(`/login?next=/interview/${interviewId}`);
        return;
      }

      if (!res.ok) {
        const msg = `Evaluation failed (${res.status})`;
        console.error(msg);
        setError(msg);
        return;
      }

      const json = await res.json();
      setData(normalizeInterview(json));
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to evaluate interview");
    } finally {
      setEvaluating(false);
    }
  };

  // Delete interview
  const handleDelete = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    const res = await fetch(
      `http://localhost:8000/interview/${interviewId}`,
      {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    if (res.status === 401) {
      localStorage.removeItem("token");
      router.push("/login");
      return;
    }

    if (res.ok) {
      router.push("/dashboard"); // go back after deleting
    } else {
      alert("Failed to delete interview");
    }
  };

  if (loading) {
    return <p className="text-gray-400 p-10">Loading interview...</p>;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black text-white p-10 space-y-4">
        <p className="text-red-400">Error: {error}</p>
        <Button
          className="bg-purple-600 hover:bg-purple-700 rounded-lg px-5 py-2"
          onClick={() => router.push("/dashboard")}
        >
          ← Back to Dashboard
        </Button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-black text-white p-10">
        <p>Interview not found.</p>
      </div>
    );
  }

  const hasEvaluation =
    typeof data.overall_score === "number" &&
    !Number.isNaN(data.overall_score) &&
    data.overall_score > 0;

  return (
    <div className="min-h-screen bg-black text-white p-10 space-y-6">
      {/* Top buttons */}
      <div className="flex flex-wrap gap-4 items-center">
        <Button
          className="bg-purple-600 hover:bg-purple-700 rounded-lg px-5 py-2"
          onClick={() => router.push("/dashboard")}
        >
          ← Back to Dashboard
        </Button>

        <Button
          className="bg-red-600 hover:bg-red-700 rounded-lg px-5 py-2"
          onClick={handleDelete}
        >
          🗑 Delete Interview
        </Button>

        {!hasEvaluation && (
          <Button
            className="bg-green-600 hover:bg-green-700 rounded-lg px-5 py-2"
            onClick={handleEvaluate}
            disabled={evaluating}
          >
            {evaluating ? "Evaluating..." : "Evaluate Interview"}
          </Button>
        )}

        {hasEvaluation && (
          <span className="text-sm text-gray-300">
            Overall score:{" "}
            <span className="font-semibold">
              {data.overall_score.toFixed(1)} / 10
            </span>
          </span>
        )}
      </div>

      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold mb-1">Interview Review</h2>
        <p className="text-sm text-gray-400">
          {data.role && <span>Role: {data.role} · </span>}
          {data.level && <span>Level: {data.level} · </span>}
          {data.type && <span>Type: {data.type} · </span>}
          {data.techstack && <span>Stack: {data.techstack}</span>}
        </p>
      </div>

      {/* Coaching summary & insights */}
      {hasEvaluation && (
        <div className="bg-gray-900 p-5 rounded-lg border border-gray-700 space-y-3">
          <h3 className="text-lg font-semibold">Coaching Summary</h3>

          {data.coaching_summary && (
            <p className="text-sm text-gray-200">{data.coaching_summary}</p>
          )}

          {Array.isArray(data.strengths) && data.strengths.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-1 text-green-400">
                Strengths
              </h4>
              <ul className="list-disc pl-5 text-sm text-gray-200">
                {data.strengths.map((s: string, i: number) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}

          {Array.isArray(data.weaknesses) && data.weaknesses.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-1 text-yellow-400">
                Weaknesses / Focus areas
              </h4>
              <ul className="list-disc pl-5 text-sm text-gray-200">
                {data.weaknesses.map((w: string, i: number) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {Array.isArray(data.coaching_tips) &&
            data.coaching_tips.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold mb-1 text-blue-400">
                  Tips for next time
                </h4>
                <ul className="list-disc pl-5 text-sm text-gray-200">
                  {data.coaching_tips.map((t: string, i: number) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </div>
            )}
        </div>
      )}

      {/* Questions & Answers + per-question evaluation */}
      <ul className="space-y-4">
        {Array.isArray(data.questions) &&
          data.questions.map((q: string, i: number) => {
            const answer = data.answers?.[i];
            const evalData = data.evaluations?.[i];

            return (
              <li
                key={i}
                className="bg-gray-900 p-4 rounded-lg border border-gray-700 space-y-2"
              >
                <p className="text-sm font-semibold">
                  <strong>Q{i + 1}:</strong> {q}
                </p>
                <p className="text-sm">
                  <strong>A:</strong>{" "}
                  {answer || (
                    <span className="italic text-gray-400">No answer</span>
                  )}
                </p>

                {evalData && (
                  <div className="mt-2 space-y-1 text-xs text-gray-300">
                    {typeof evalData.overall_score === "number" && (
                      <p>
                        <span className="font-semibold">Score:</span>{" "}
                        {evalData.overall_score.toFixed(1)} / 10
                      </p>
                    )}

                    {evalData.criteria && (
                      <div className="space-y-0.5 text-gray-400">
                        {Object.entries(evalData.criteria).map(
                          ([name, value]) =>
                            typeof value === "number" && (
                              <div key={name}>
                                {name}: {value.toFixed(1)} / 10
                              </div>
                            )
                        )}
                      </div>
                    )}

                    {Array.isArray(evalData.strengths) &&
                      evalData.strengths.length > 0 && (
                        <p>
                          <span className="font-semibold">Strengths:</span>{" "}
                          {evalData.strengths.join(", ")}
                        </p>
                      )}

                    {Array.isArray(evalData.weaknesses) &&
                      evalData.weaknesses.length > 0 && (
                        <p>
                          <span className="font-semibold">Weaknesses:</span>{" "}
                          {evalData.weaknesses.join(", ")}
                        </p>
                      )}
                  </div>
                )}
              </li>
            );
          })}
      </ul>
    </div>
  );
}
