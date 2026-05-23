import { API_URL } from "@/lib/api";

export default async function ReviewDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const review = await fetch(`${API_URL}/api/reviews/${id}`, { cache: "no-store" }).then((res) => res.json());
  return (
    <main>
      <header className="topbar">
        <span>{review.repo}</span>
        <small>Review #{id}</small>
      </header>
      <pre className="detailJson">{JSON.stringify(review, null, 2)}</pre>
    </main>
  );
}
