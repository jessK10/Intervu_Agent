import { NextResponse } from "next/server";
import { generateInterviewQuestions } from "@/lib/openai"; // 

export async function POST(request: Request) {
  try {
    const { role, level, type, techstack, amount, userid } = await request.json();

    if (!role || !level || !type || !techstack || !amount) {
      return NextResponse.json(
        { success: false, error: "Missing required fields" },
        { status: 400 }
      );
    }

    // 🔹 Call Gemini → always returns string[]
    const questions = await generateInterviewQuestions({
      role,
      level,
      type,
      techstack,
      amount,
      userid,
    });

    if (!questions.length) {
      return NextResponse.json(
        { success: false, error: "No questions generated" },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true, questions });
  } catch (err: any) {
    console.error("❌ API error:", err);
    return NextResponse.json(
      { success: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
