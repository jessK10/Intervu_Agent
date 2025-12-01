"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { getToken } from "@/lib/auth";

type Profile = {
    headline: string;
    education: any[];
    experience: any[];
    projects: any[];
    skills: {
        hard_skills: string[];
        soft_skills: string[];
    };
    strengths: string[];
    weaknesses: string[];
};

export default function CareerApplyPage() {
    const router = useRouter();
    const [profile, setProfile] = useState<Profile | null>(null);
    const [jobInput, setJobInput] = useState("");
    const [inputType, setInputType] = useState<"url" | "text">("text");

    const [loading, setLoading] = useState(false);
    const [jobData, setJobData] = useState<any>(null);
    const [tailoredResume, setTailoredResume] = useState<any>(null);
    const [motivationLetter, setMotivationLetter] = useState("");
    const [messages, setMessages] = useState<any>(null);

    // Load profile
    useEffect(() => {
        const loadProfile = async () => {
            const token = getToken();
            if (!token) {
                router.push("/login?next=/career/apply");
                return;
            }

            try {
                const res = await fetch("http://localhost:8000/profile/me", {
                    headers: { Authorization: `Bearer ${token}` },
                });

                if (!res.ok) {
                    alert("Please set up your profile first");
                    router.push("/profile/setup");
                    return;
                }

                const data = await res.json();

                if (!data) {
                    alert("Please set up your profile first");
                    router.push("/profile/setup");
                    return;
                }

                setProfile(data);
            } catch (err) {
                alert("Please set up your profile first");
                router.push("/profile/setup");
            }
        };

        loadProfile();
    }, [router]);

    const handleAnalyzeJob = async () => {
        const token = getToken();
        if (!token || !jobInput.trim()) return;

        setLoading(true);

        try {
            const payload =
                inputType === "url"
                    ? { job_url: jobInput }
                    : { job_text: jobInput };

            const res = await fetch("http://localhost:8000/career/analyze-job", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(payload),
            });

            if (res.ok) {
                const data = await res.json();
                setJobData(data);
            } else {
                alert("Failed to analyze job");
            }
        } catch (err) {
            console.error(err);
            alert("Error analyzing job");
        } finally {
            setLoading(false);
        }
    };

    const handleTailorResume = async () => {
        const token = getToken();
        if (!token || !jobData) return;

        setLoading(true);

        try {
            const res = await fetch("http://localhost:8000/career/tailor-resume", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(jobData),
            });

            if (res.ok) {
                const data = await res.json();
                setTailoredResume(data);
            } else {
                alert("Failed to generate resume");
            }
        } catch (err) {
            console.error(err);
            alert("Error generating resume");
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateLetter = async () => {
        const token = getToken();
        if (!token || !jobData) return;

        setLoading(true);

        try {
            const res = await fetch("http://localhost:8000/career/generate-letter", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ job_data: jobData, tone: "professional" }),
            });

            if (res.ok) {
                const data = await res.json();
                setMotivationLetter(data.letter);
            } else {
                alert("Failed to generate letter");
            }
        } catch (err) {
            console.error(err);
            alert("Error generating letter");
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateMessages = async () => {
        const token = getToken();
        if (!token || !jobData || !tailoredResume) return;

        setLoading(true);

        try {
            const res = await fetch("http://localhost:8000/career/generate-messages", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    job_data: jobData,
                    tailored_resume: tailoredResume,
                }),
            });

            if (res.ok) {
                const data = await res.json();
                setMessages(data);
            } else {
                alert("Failed to generate messages");
            }
        } catch (err) {
            console.error(err);
            alert("Error generating messages");
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        alert("✅ Copied to clipboard!");
    };

    return (
        <div className="min-h-screen bg-black text-white px-8 py-12">
            <div className="max-w-6xl mx-auto space-y-8">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Apply to Job</h1>
                    <p className="text-gray-400">
                        AI-powered career tools to create tailored applications
                    </p>
                </div>

                {/* Job Input */}
                <Card className="bg-gray-900 border-gray-700">
                    <CardHeader>
                        <CardTitle>Step 1: Enter Job Description</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex gap-4">
                            <Button
                                onClick={() => setInputType("text")}
                                variant={inputType === "text" ? "default" : "outline"}
                                className={inputType === "text" ? "bg-purple-600" : ""}
                            >
                                Paste Text
                            </Button>
                            <Button
                                onClick={() => setInputType("url")}
                                variant={inputType === "url" ? "default" : "outline"}
                                className={inputType === "url" ? "bg-purple-600" : ""}
                            >
                                Job URL
                            </Button>
                        </div>

                        {inputType === "text" ? (
                            <textarea
                                value={jobInput}
                                onChange={(e) => setJobInput(e.target.value)}
                                placeholder="Paste the job description here..."
                                className="w-full h-48 p-4 bg-gray-800 border border-gray-600 rounded-lg text-white resize-y"
                            />
                        ) : (
                            <input
                                type="url"
                                value={jobInput}
                                onChange={(e) => setJobInput(e.target.value)}
                                placeholder="https://linkedin.com/jobs/..."
                                className="w-full p-3 bg-gray-800 border border-gray-600 rounded-lg text-white"
                            />
                        )}

                        <Button
                            onClick={handleAnalyzeJob}
                            disabled={loading || !jobInput.trim()}
                            className="bg-purple-600 hover:bg-purple-700"
                        >
                            {loading ? "Analyzing..." : "Analyze Job"}
                        </Button>
                    </CardContent>
                </Card>

                {/* Job Summary */}
                {jobData && (
                    <Card className="bg-gray-900 border-gray-700">
                        <CardHeader>
                            <CardTitle>✅ Job Summary</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <p className="text-2xl font-bold">{jobData.job_title}</p>
                                <p className="text-gray-400">{jobData.company}</p>
                                {jobData.job_url && (
                                    <a
                                        href={jobData.job_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-400 hover:text-blue-300 text-sm underline mt-1 block"
                                    >
                                        View Job Posting ↗
                                    </a>
                                )}

                                {(jobData.job_title === "Unknown" || jobData.company === "Unknown") && (
                                    <div className="mt-4 p-3 bg-yellow-900/30 border border-yellow-700/50 rounded text-yellow-200 text-sm">
                                        ⚠️ <strong>Analysis Incomplete?</strong>
                                        <p className="mt-1">
                                            We couldn't fully extract details from the URL. This often happens with sites like LinkedIn/Indeed that block automated access.
                                        </p>
                                        <Button
                                            variant="link"
                                            className="text-yellow-400 p-0 h-auto mt-2 underline"
                                            onClick={() => {
                                                setJobData(null);
                                                setInputType("text");
                                            }}
                                        >
                                            Try pasting the job description text instead →
                                        </Button>
                                    </div>
                                )}
                            </div>

                            <div>
                                <h4 className="font-semibold mb-2">Required Skills:</h4>
                                <div className="flex flex-wrap gap-2">
                                    {jobData.job_requirements?.hard_skills?.map((skill: string) => (
                                        <span
                                            key={skill}
                                            className="px-3 py-1 bg-blue-600/20 text-blue-300 rounded-full text-xs"
                                        >
                                            {skill}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <Button
                                    onClick={handleTailorResume}
                                    disabled={loading}
                                    className="bg-green-600 hover:bg-green-700"
                                >
                                    Generate Tailored Resume
                                </Button>
                                <Button
                                    onClick={handleGenerateLetter}
                                    disabled={loading}
                                    className="bg-blue-600 hover:bg-blue-700"
                                >
                                    Generate Cover Letter
                                </Button>
                                {tailoredResume && (
                                    <Button
                                        onClick={handleGenerateMessages}
                                        disabled={loading}
                                        className="bg-orange-600 hover:bg-orange-700"
                                    >
                                        Generate Messages
                                    </Button>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Tailored Resume */}
                {tailoredResume && (
                    <Card className="bg-gray-900 border-gray-700">
                        <CardHeader>
                            <div className="flex justify-between items-center">
                                <CardTitle>📄 Tailored Resume</CardTitle>
                                <Button
                                    onClick={() => copyToClipboard(JSON.stringify(tailoredResume, null, 2))}
                                    size="sm"
                                    className="bg-gray-700"
                                >
                                    Copy
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <h4 className="font-semibold text-sm text-gray-400 mb-2">
                                    Professional Summary
                                </h4>
                                <p className="text-white">{tailoredResume.summary}</p>
                            </div>

                            {tailoredResume.experience?.map((exp: any, i: number) => (
                                <div key={i}>
                                    <p className="font-semibold">{exp.title}</p>
                                    <p className="text-sm text-gray-400">{exp.company}</p>
                                    <ul className="list-disc list-inside mt-2 space-y-1 text-sm">
                                        {exp.bullets?.map((bullet: string, j: number) => (
                                            <li key={j} className="text-gray-300">
                                                {bullet}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                )}

                {/* Motivation Letter */}
                {motivationLetter && (
                    <Card className="bg-gray-900 border-gray-700">
                        <CardHeader>
                            <div className="flex justify-between items-center">
                                <CardTitle>✉️ Cover Letter</CardTitle>
                                <Button
                                    onClick={() => copyToClipboard(motivationLetter)}
                                    size="sm"
                                    className="bg-gray-700"
                                >
                                    Copy
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <pre className="whitespace-pre-wrap font-sans text-white">
                                {motivationLetter}
                            </pre>
                        </CardContent>
                    </Card>
                )}

                {/* Messages */}
                {messages && (
                    <Card className="bg-gray-900 border-gray-700">
                        <CardHeader>
                            <CardTitle>📧 Application Messages</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <h4 className="font-semibold">Email Subject</h4>
                                    <Button
                                        onClick={() => copyToClipboard(messages.email_subject)}
                                        size="sm"
                                        className="bg-gray-700"
                                    >
                                        Copy
                                    </Button>
                                </div>
                                <p className="text-gray-300">{messages.email_subject}</p>
                            </div>

                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <h4 className="font-semibold">Email Body</h4>
                                    <Button
                                        onClick={() => copyToClipboard(messages.email_body)}
                                        size="sm"
                                        className="bg-gray-700"
                                    >
                                        Copy
                                    </Button>
                                </div>
                                <pre className="whitespace-pre-wrap font-sans text-gray-300">
                                    {messages.email_body}
                                </pre>
                            </div>

                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <h4 className="font-semibold">LinkedIn Connection Note</h4>
                                    <Button
                                        onClick={() => copyToClipboard(messages.linkedin_note)}
                                        size="sm"
                                        className="bg-gray-700"
                                    >
                                        Copy
                                    </Button>
                                </div>
                                <p className="text-gray-300">{messages.linkedin_note}</p>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
