"use client";

import { useEffect, useState } from "react";
import { AgentPipeline } from "@/components/AgentPipeline";
import { FindingsList } from "@/components/FindingsList";
import { GitHubCommentPreview } from "@/components/GitHubCommentPreview";
import { ManualTrigger } from "@/components/ManualTrigger";
import { ReviewCard } from "@/components/ReviewCard";
import { fetchReviews, type ReviewReport } from "@/lib/api";

export default function Home() {
  const [reviews, setReviews] = useState<ReviewReport[]>([]);
  const [selected, setSelected] = useState<ReviewReport | null>(null);

  useEffect(() => {
    fetchReviews().then((items) => {
      setReviews(items);
      setSelected(items[0] || null);
    });
  }, []);

  function handleReview(review: ReviewReport) {
    setSelected(review);
    setReviews((current) => [review, ...current.filter((item) => item.id !== review.id)].slice(0, 5));
  }

  return (
    <main>
      <header className="topbar">
        <span>ERP DevOps GitAgent</span>
        <small>Powered by GitAgent + Claude-ready agents</small>
      </header>
      <ManualTrigger onReview={handleReview} />
      <AgentPipeline trail={selected?.agent_trail || []} />
      <section className="recent">
        <h2>Recent Reviews</h2>
        <div className="reviewGrid">
          {reviews.slice(0, 5).map((review) => (
            <ReviewCard key={review.id || `${review.repo}-${review.pr_number}`} review={review} onSelect={setSelected} />
          ))}
        </div>
      </section>
      <section className="reviewPanel">
        <FindingsList
          critical={selected?.critical || []}
          warnings={selected?.warnings || []}
          suggestions={selected?.suggestions || []}
        />
        <GitHubCommentPreview markdown={selected?.comment_markdown || ""} />
      </section>
    </main>
  );
}
