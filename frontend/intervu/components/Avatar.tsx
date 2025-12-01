"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import md5 from "md5";

type AvatarProps = {
  email: string;
  name?: string;
  size?: number;
};

function getGravatarUrl(email: string, size: number) {
  const hash = md5(email.trim().toLowerCase());
  return `https://www.gravatar.com/avatar/${hash}?d=404&s=${size}`;
}

export default function Avatar({ email, name, size = 80 }: AvatarProps) {
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  // ✅ Normalize display name (no fallback to id)
  const displayName = name?.trim() || email.split("@")[0] || "User";

  useEffect(() => {
    const checkGravatar = async () => {
      const url = getGravatarUrl(email, size);
      try {
        const res = await fetch(url);
        if (res.ok) {
          setAvatarUrl(url);
        } else {
          setAvatarUrl(null);
        }
      } catch {
        setAvatarUrl(null);
      }
    };
    if (email) checkGravatar();
  }, [email, size]);

  if (avatarUrl) {
    return (
      <Image
        src={avatarUrl}
        alt={displayName}
        width={size}
        height={size}
        className="rounded-full"
      />
    );
  }

  return (
    <div
      className="flex items-center justify-center rounded-full bg-indigo-600 text-white font-bold"
      style={{ width: size, height: size, fontSize: size / 2 }}
    >
      {displayName.charAt(0).toUpperCase()}
    </div>
  );
}
