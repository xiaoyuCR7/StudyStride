/**
 * Hero background video URLs from `public/p.md` (SECTION 1: HERO — Background video).
 * Prefer `public/prisma-hero-bg.mp4`; on load error fall back to CDN.
 */
export const HERO_VIDEO_CDN =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260405_170732_8a9ccda6-5cff-4628-b164-059c500a2b41.mp4'

export function heroVideoLocalUrl(): string {
  const base = import.meta.env.BASE_URL || '/'
  const normalized = base.endsWith('/') ? base : `${base}/`
  return `${normalized}prisma-hero-bg.mp4`
}

/** `public/hero-video.mp4` — landing page hero only */
export function landingHeroVideoLocalUrl(): string {
  const base = import.meta.env.BASE_URL || '/'
  const normalized = base.endsWith('/') ? base : `${base}/`
  return `${normalized}hero-video.mp4`
}
