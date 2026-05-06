import { Helmet } from "react-helmet-async";

type SeoProps = {
  title: string;
  description: string;
  canonical?: string;
  noindex?: boolean;
  ogTitle?: string;
  ogDescription?: string;
};

export default function Seo({
  title,
  description,
  canonical,
  noindex = false,
  ogTitle,
  ogDescription,
}: SeoProps) {
  const siteUrl = "http://localhost:5173";
  const canonicalUrl = canonical ? `${siteUrl}${canonical}` : siteUrl;

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />

      {noindex ? (
        <meta name="robots" content="noindex, nofollow" />
      ) : (
        <meta name="robots" content="index, follow" />
      )}

      <link rel="canonical" href={canonicalUrl} />

      <meta property="og:title" content={ogTitle || title} />
      <meta property="og:description" content={ogDescription || description} />
      <meta property="og:type" content="website" />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:site_name" content="Whisper Mood" />
    </Helmet>
  );
}