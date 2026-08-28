const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function generatePlan(payload: unknown) {
  const res = await fetch(`${BASE}/api/plans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`plan_failed: ${res.status}`);
  return res.json();
}

export async function scoreMock(payload: unknown) {
  const res = await fetch(`${BASE}/api/mock-sessions/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`score_failed: ${res.status}`);
  return res.json();
}
