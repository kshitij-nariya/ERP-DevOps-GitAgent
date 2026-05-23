import type { ReviewReport } from "@/lib/api";

export function ReviewCard({ review, onSelect }: { review: ReviewReport; onSelect: (review: ReviewReport) => void }) {
  return (
    <button className="reviewCard" onClick={() => onSelect(review)}>
      <span>{review.repo}</span>
      <strong>{review.critical_count} critical</strong>
      <small>{review.files_reviewed} files reviewed</small>
    </button>
  );
}
