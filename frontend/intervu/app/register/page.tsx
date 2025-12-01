"use client";

export const dynamic = "force-dynamic";

import { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import Image from "next/image";

export default function RegisterPageContent() {
  const searchParams = useSearchParams();
  const nextUrl = searchParams.get("next");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      // ✅ Register
      const res = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      if (res.status === 409) throw new Error("User already exists");
      if (!res.ok) throw new Error("Registration failed");

      // ✅ Auto-login
      const loginRes = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!loginRes.ok) throw new Error("Auto-login failed");

      const loginData = await loginRes.json();
      localStorage.setItem("token", loginData.access_token);

      // ✅ notify Navbar/useUser immediately
      window.dispatchEvent(new Event("storage"));

      setSuccess("Account created successfully! Redirecting...");

      setTimeout(() => {
        window.location.href = nextUrl || "/dashboard";
      }, 1200);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-black bg-center bg-repeat relative"
      style={{ backgroundImage: "url('/pattern.png')" }}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />

      <Card className="w-full max-w-md bg-white/10 backdrop-blur-md text-white shadow-2xl rounded-2xl border border-gray-700 relative z-10 animate-fadeIn">
        <CardHeader className="flex flex-col items-center gap-2">
          <Image
            src="/logo.svg"
            alt="InterVU Logo"
            width={60}
            height={60}
            className="mb-2"
          />
          <CardTitle className="text-center text-3xl font-bold">InterVU</CardTitle>
          <CardDescription className="text-center text-gray-300">
            Create your account
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleRegister}>
          <CardContent className="space-y-4">
            {error && <p className="text-red-400 text-sm text-center">{error}</p>}
            {success && <p className="text-green-400 text-sm text-center">{success}</p>}

            <div>
              <label className="block text-sm text-gray-300 mb-1">Name</label>
              <Input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="bg-white/20 border-gray-600 text-white placeholder-gray-300"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-300 mb-1">Email</label>
              <Input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-white/20 border-gray-600 text-white placeholder-gray-300"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-300 mb-1">Password</label>
              <Input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-white/20 border-gray-600 text-white placeholder-gray-300"
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col gap-3">
            <Button
              type="submit"
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl"
              disabled={loading}
            >
              {loading ? "Creating..." : "Create an Account"}
            </Button>

            <p className="text-sm text-gray-300 text-center">
              Have an account already?{" "}
              <Link
                href="/login"
                className="text-purple-400 font-medium hover:underline"
              >
                Sign In
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
