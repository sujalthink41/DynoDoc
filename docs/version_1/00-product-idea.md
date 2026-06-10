# DynoDoc — Product Idea (v1)

> **One line:** DynoDoc is an AI-native learning platform that turns *"I want to learn X"* into a personalized, Udemy-style course — with lessons written for **you**, a tutor that answers your questions, and tasks that **verify you actually learned it**.

---

## 1. The Problem

Learning something new on your own today is broken:

- **Too many resources, no path.** You google "learn Python", get 10,000 links, and don't know the order to learn things in.
- **Content isn't made for you.** A course assumes everyone is the same. A working JavaScript developer and a total beginner get the *exact same lessons*.
- **No one checks if you actually learned it.** You watch videos, feel productive, and three weeks later you've built nothing and remember nothing.
- **You give up.** Most people quit online courses in the first week because there's no momentum and no proof of progress.

Free roadmaps (like roadmap.sh) and ChatGPT can give you a list of topics. But nobody **teaches you, adapts to you, and verifies you** — all in one place.

---

## 2. The Idea

You tell DynoDoc what you want to learn. It asks you a few quick questions to understand your background and goal. Then its AI builds you a **complete, structured course**:

- A **roadmap** broken into **lectures** (like a Udemy course outline).
- Each lecture has **well-written docs** — clear lessons that actually teach the concept.
- Each lecture has **curated reference links and YouTube suggestions** to go deeper.
- After each lecture, a **quiz and a hands-on coding task** to prove you learned it.
- A **right-side AI tutor** you can chat with anytime about what you're reading.

You read, you ask questions, you build, you get verified, you move on. You can save lectures and track how far you've come.

**The key difference from everyone else:** the lessons are **generated and adapted for you**, and the platform **checks your work** instead of just trusting you watched a video.

---

## 3. Who It's For (v1)

**Self-learners (B2C)** — individuals teaching themselves a skill on their own time.

> We're starting here because it's the biggest audience and the best place to prove the product. The same engine can later serve developers upskilling and companies training teams — but v1 is focused on the solo learner.

---

## 4. Why DynoDoc Is Different

What makes this **AI-native**, not just "a course site with a chatbot bolted on":

| Most platforms (Udemy, Coursera) | DynoDoc |
|----------------------------------|---------|
| One static course for everyone | Lessons **generated and tuned to your level and background** |
| You watch passively | You read, ask, and **build** |
| No one checks your work | AI **grades your code** and verifies you learned it |
| Generic Q&A forum | A tutor **grounded in the exact lesson you're reading** |
| You're on your own | Progress tracking that keeps you moving |

A static course **physically cannot** rewrite itself for a JavaScript developer learning Python. DynoDoc can. That's the whole bet.

---

## 5. The "Wow" Feature for v1: Lessons Made For You

This is the headline feature that makes people say *"whoa"*:

**The lessons adapt to who you are.**

- A JavaScript developer learning Python sees concepts explained **using JavaScript analogies**.
- A complete beginner gets simpler explanations and more examples.
- Reading something too hard? **"Explain this simpler."** The lesson rewrites itself.
- Already know this? **"Go deeper."** It levels up.

No other learning platform can do this, because their content is pre-recorded and fixed. Ours is generated.

---

## 6. The Moat (Why This Gets Harder to Copy Over Time)

Anyone can prompt an AI to make a roadmap this weekend. That's not defensible. What *is* defensible:

1. **The verification loop.** We don't just teach — we check your code with AI and confirm you learned it. This is hard to build and is the real value.
2. **The learner model.** Every quiz answer, every coding task, every "I'm confused about X" builds a picture of what *you* actually know. Lessons and tutoring get more personal over time.
3. **The growing knowledge base.** Every course we generate makes our vetted content library bigger and better — so future courses get faster, cheaper, and higher quality. It compounds.

The roadmap is the demo. **The verify-and-adapt loop is the business.**

---

## 7. What's In v1 (Scope)

The goal of v1 is **one skill, done excellently** — a complete, polished vertical slice that proves the whole experience.

**In scope for v1:**

- ✅ Short intake (3–5 questions) to understand the learner.
- ✅ AI-generated **roadmap → lectures → docs** for the chosen skill.
- ✅ **Curated reference links + YouTube** suggestions per topic.
- ✅ **Right-side AI tutor** grounded in the current lesson.
- ✅ **Quiz + one AI-graded coding task** per lecture (the verification moat).
- ✅ **Progress tracking** and **save lectures**.
- ✅ **Wow feature:** lessons adapt to the learner's level/background ("explain simpler / go deeper").
- ✅ Data foundation built so personalization & the knowledge base can grow later.

**Deliberately parked for later (NOT in v1):**

- ⏸️ Self-rewriting "living" roadmap that re-plans based on performance.
- ⏸️ Critic agent that auto-reviews and improves generated content.
- ⏸️ Cross-learner insights ("others got stuck here").
- ⏸️ Voice, mobile, verified credentials/certificates.
- ⏸️ Multi-skill scale, teams/enterprise, social features.

> Parking these keeps v1 shippable. They are roadmap items, not deleted ideas.

---

## 8. The Core Loop (How a User Experiences It)

```
1. "I want to learn Python."
2. Answer 3–5 quick questions (background, goal, level).
3. DynoDoc builds your course: roadmap → lectures → docs.
4. Open Lecture 1. Read the docs (written for your level).
5. Stuck? Ask the AI tutor on the right — it knows this exact lesson.
6. Too hard / too easy? Tap "simpler" / "deeper" — the lesson adapts.
7. End of lecture: take the quiz + complete the coding task.
8. AI grades your code → you're verified → progress updates.
9. Save the lecture, move to the next. Repeat.
```

---

## 9. Tech Direction (high level — details in a later doc)

- **Frontend:** Next.js (React)
- **Backend / API:** FastAPI
- **AI orchestration:** Google ADK (multi-agent — for course generation + the runtime tutor/grader)
- **Retrieval:** RAG (grounding the tutor, building the knowledge base, personalizing per learner)
- **Database:** PostgreSQL (+ pgvector for retrieval)
- **Code grading:** sandboxed execution

> The detailed architecture — which agents exist, which RAG layers do what — gets its own doc next.

---

## 10. Success Criteria for v1

v1 is a win if a real person can:

1. Ask to learn a skill and get a course that feels **genuinely tailored to them**.
2. Read a lesson, get a confused moment answered by the tutor, and feel unblocked.
3. Adapt a lesson's difficulty and feel it actually change.
4. Complete a coding task, get it **graded by AI**, and feel *"okay, I really learned that."*

If those four moments feel magical, we have something worth building on.
