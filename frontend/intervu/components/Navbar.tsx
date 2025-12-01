"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useUser } from "@/lib/useUser";
import Avatar from "@/components/Avatar";

export default function Navbar() {
  const { user, loading, refetch } = useUser();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.dispatchEvent(new Event("storage")); // ✅ refresh state immediately
    router.push("/login");
  };

  return (
    <nav className="flex justify-between items-center p-4 bg-black text-white border-b border-gray-800">
      {/* Left: Logo + Links */}
      <div className="flex items-center gap-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <img src="/logo.svg" alt="InterVU" className="h-12 w-12" />
          <span className="font-bold text-xl">InterVU</span>
        </Link>

        {user && (
          <div className="flex items-center gap-4 ml-4">
            <Link
              href="/dashboard"
              className="text-sm text-gray-300 hover:text-white transition"
            >
              Interviews
            </Link>
            <Link
              href="/career/apply"
              className="text-sm text-gray-300 hover:text-white transition"
            >
              Career Tools
            </Link>
            <Link
              href="/profile/setup"
              className="text-sm text-gray-300 hover:text-white transition"
            >
              Profile
            </Link>
          </div>
        )}
      </div>

      {/* Right: User */}
      {loading ? (
        <div className="text-gray-400">Loading...</div>
      ) : user ? (
        <div className="flex items-center gap-3">
          <Avatar name={user.name} email={user.email} size={40} />
          <span className="text-sm text-gray-300">{user.name || user.email}</span>
          <button
            onClick={handleLogout}
            className="text-red-400 hover:text-red-500 text-sm"
          >
            Logout
          </button>
        </div>
      ) : (
        <Link href="/login" className="text-sm text-gray-300">
          Login
        </Link>
      )}

    </nav>
  );
}
