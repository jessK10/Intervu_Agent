"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { getToken } from "@/lib/auth";

export default function ProfileSetupPage() {
    const router = useRouter();
    const [cvText, setCvText] = useState("");
    const [loading, setLoading] = useState(false);
    const [profile, setProfile] = useState<any>(null);

    // Load existing profile if exists
    useEffect(() => {
        const loadProfile = async () => {
            const token = getToken();
            if (!token) {
                router.push("/login?next=/profile/setup");
                return;
            }

            try {
                const res = await fetch("http://localhost:8000/profile/me", {
                    headers: { Authorization: `Bearer ${token}` },
                });

                if (res.ok) {
                    const data = await res.json();
                    if (data) {
                        setProfile(data);
                        setCvText(data.cv_text || "");
                    }
                }
            } catch (err) {
                console.log("No existing profile");
            }
        };

        loadProfile();
    }, [router]);

    const handleParseCV = async () => {
        const token = getToken();
        if (!token) {
            router.push("/login");
            return;
        }

        if (!cvText.trim()) {
            alert("Please enter your CV text");
            return;
        }

        setLoading(true);

        try {
            const res = await fetch("http://localhost:8000/profile/upload-cv", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ cv_text: cvText }),
            });

            if (res.ok) {
                const data = await res.json();
                setProfile(data);
                alert("✅ CV parsed successfully!");
            } else {
                const err = await res.json();
                alert(`❌ Error: ${err.detail}`);
            }
        } catch (err) {
            console.error(err);
            alert("Failed to parse CV");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white px-8 py-12">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold mb-2">Career Profile Setup</h1>
                    <p className="text-gray-400">
                        Upload your CV to get started with personalized career tools
                    </p>
                </div>

                {/* CV Input */}
                <Card className="bg-gray-900 border-gray-700">
                    <CardHeader>
                        <CardTitle>Upload Your CV</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <textarea
                            value={cvText}
                            onChange={(e) => setCvText(e.target.value)}
                            placeholder="Paste your CV text here...

Example:
John Doe
Software Engineer

Education:
- Bachelor of Computer Science, XYZ University (2020)

Experience:
- Software Engineer at ABC Corp (2020-2023)
  • Built React applications
  • Led team of 3 developers

Skills: Python, React, Node.js, MongoDB"
                            className="w-full h-64 p-4 bg-gray-800 border border-gray-600 rounded-lg text-white font-mono text-sm resize-y"
                        />

                        <Button
                            onClick={handleParseCV}
                            disabled={loading || !cvText.trim()}
                            className="bg-purple-600 hover:bg-purple-700"
                        >
                            {loading ? "Parsing with AI..." : "Parse CV with AI"}
                        </Button>
                    </CardContent>
                </Card>

                {/* Parsed Profile */}
                {profile && (
                    <Card className="bg-gray-900 border-gray-700">
                        <CardHeader>
                            <CardTitle>✅ Parsed Profile</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Headline */}
                            {profile.headline && (
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-400 mb-2">
                                        Headline
                                    </h3>
                                    <p className="text-white">{profile.headline}</p>
                                </div>
                            )}

                            {/* Education */}
                            {profile.education && profile.education.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-400 mb-2">
                                        Education
                                    </h3>
                                    <div className="space-y-2">
                                        {profile.education.map((edu: any, i: number) => (
                                            <div key={i} className="text-sm">
                                                <p className="text-white font-medium">
                                                    {edu.degree} in {edu.field}
                                                </p>
                                                <p className="text-gray-400">
                                                    {edu.institution} ({edu.graduation_year})
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Experience */}
                            {profile.experience && profile.experience.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-400 mb-2">
                                        Experience
                                    </h3>
                                    <div className="space-y-3">
                                        {profile.experience.map((exp: any, i: number) => (
                                            <div key={i} className="text-sm">
                                                <p className="text-white font-medium">{exp.title}</p>
                                                <p className="text-gray-400">
                                                    {exp.company} | {exp.start_date} -{" "}
                                                    {exp.end_date || "Present"}
                                                </p>
                                                {exp.bullets && exp.bullets.length > 0 && (
                                                    <ul className="list-disc list-inside mt-1 text-gray-300 space-y-1">
                                                        {exp.bullets.map((bullet: string, j: number) => (
                                                            <li key={j}>{bullet}</li>
                                                        ))}
                                                    </ul>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Skills */}
                            {profile.skills && (
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-400 mb-2">
                                        Skills
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {profile.skills.hard_skills?.map((skill: string) => (
                                            <span
                                                key={skill}
                                                className="px-3 py-1 bg-purple-600/20 text-purple-300 rounded-full text-xs border border-purple-500/30"
                                            >
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <Button
                                onClick={() => router.push("/career/apply")}
                                className="bg-green-600 hover:bg-green-700"
                            >
                                Apply to Job →
                            </Button>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
