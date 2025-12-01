"use client";

import Image from "next/image";
import Link from "next/link";
import { isLoggedIn, logout } from "@/lib/auth";

export default function Header() {
  const loggedIn = isLoggedIn();

  return (
    <header className="sticky top-0 z-50 bg-black/80 backdrop-blur-md border-b border-gray-800 px-6 py-4 flex items-center justify-between">
      {/* Left Logo */}
      <div className="flex items-center gap-2">
        <Image src="/logo.svg" alt="InterVU Logo" width={36} height={36} />
        <h1 className="text-xl font-bold">InterVU</h1>
      </div>

      {/* Right side */}
      <div>
        {loggedIn ? (
          <div className="flex items-center gap-4">
            {/* User Avatar (static or later from DB) */}
            <Image
              src="/user-avatar.png" // <-- put your login symbol image in public/
              alt="User Avatar"
              width={36}
              height={36}
              className="rounded-full border border-gray-600 cursor-pointer hover:scale-105 transition"
              onClick={logout} // 🔥 click to logout
            />
          </div>
        ) : (
          <Link
            href="/login"
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium text-white"
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
}
