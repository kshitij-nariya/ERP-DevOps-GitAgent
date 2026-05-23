export function GitHubCommentPreview({ markdown }: { markdown: string }) {
  return (
    <section className="commentPreview">
      <h2>GitHub Comment Preview</h2>
      <pre>{markdown || "Run a review to generate the PR comment."}</pre>
    </section>
  );
}
