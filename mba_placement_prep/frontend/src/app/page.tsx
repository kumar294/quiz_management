export default function Home() {
  return (
    <main style={{ maxWidth: 720, margin: "3rem auto", fontFamily: "system-ui" }}>
      <h1>GLIM Placement Prep</h1>
      <p>
        Multi-agent prep-plan generator. Pick a target company, paste the JD, upload your
        resume, and get a company-specific plan in minutes.
      </p>
      <p>
        <a href="/plans/new">Generate a prep plan →</a>
      </p>
    </main>
  );
}
