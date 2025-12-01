import { NextRequest, NextResponse } from "next/server";
import { generateInterviewQuestions } from "@/lib/gemini";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const {
      role,
      level,
      type,
      techstack,
      amount,
      userid,
    } = body ?? {};

    // basic validation
    if (!role || !level || !type || !techstack) {
      return NextResponse.json(
        { success: false, error: "Missing required fields" },
        { status: 400 }
      );
    }

    const questionCount =
      typeof amount === "number" && !Number.isNaN(amount)
        ? amount
        : 5;

    const questions = await generateInterviewQuestions({
      role,
      level,
      type,
      techstack,
      amount: questionCount,
      userid,
    });

    if (!questions || !questions.length) {
      return NextResponse.json(
        { success: false, error: "No questions generated" },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { success: true, questions },
      { status: 200 }
    );
  } catch (err: any) {
    console.error("❌ API error in /api/vapi/generate:", err);
    return NextResponse.json(
      { success: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
