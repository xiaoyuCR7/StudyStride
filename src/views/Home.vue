<template>
  <div class="hero-section">
    <div class="hero-section__bg" aria-hidden="true">
      <video
        class="hero-section__video"
        autoplay
        muted
        loop
        playsinline
        :src="landingVideoSrc"
        @error="onLandingVideoError"
      />
    </div>
    <div class="content">
      <div class="hero-content">
        <h1 class="hero-heading">
          <span class="hero-line1">Become</span>
          <span class="hero-line2">Better Every Day</span>
        </h1>
        <router-link to="/study" class="cta-button">
          Start Your Journey
          <svg class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { landingHeroVideoLocalUrl } from '../lib/heroBackgroundVideo'
import landingVideoAsset from '../assets/hero-video.mp4'

const landingVideoSrc = ref(landingHeroVideoLocalUrl())
let landingFallbackTried = false

const onLandingVideoError = () => {
  if (!landingFallbackTried && landingVideoSrc.value !== landingVideoAsset) {
    landingFallbackTried = true
    landingVideoSrc.value = landingVideoAsset
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

.hero-section {
  position: relative;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background: #000000;
  font-family: 'Almarai', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.hero-section__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.hero-section__video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.02);
}

.content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 1rem;
}

.hero-heading {
  line-height: 0.85;
  letter-spacing: -0.02em;
  margin-bottom: 2.5rem;
}

.hero-line1 {
  display: block;
  color: white;
  font-weight: 500;
  font-size: 3rem;
}

.hero-line2 {
  display: block;
  font-weight: 500;
  font-size: 3rem;
  background: linear-gradient(90deg, #64CEFB, #ffffff, #64CEFB);
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shine 3s linear infinite;
}

@keyframes shine {
  0% {
    background-position: 200% center;
  }
  100% {
    background-position: -200% center;
  }
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: black;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 9999px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.cta-button:hover {
  background-color: #1f2937;
}

.cta-button:hover .arrow {
  transform: translateX(4px);
}

.arrow {
  width: 0.875rem;
  height: 0.875rem;
  transition: transform 0.3s ease;
}

.arrow path {
  fill: currentColor;
}

@media (min-width: 640px) {
  .hero-line1,
  .hero-line2 {
    font-size: 4rem;
  }
}

@media (min-width: 768px) {
  .hero-line1,
  .hero-line2 {
    font-size: 5rem;
  }

  .cta-button {
    padding: 0.75rem 2rem;
    font-size: 1rem;
  }
}

@media (min-width: 1024px) {
  .nav-links {
    display: flex;
  }

  .hamburger {
    display: none;
  }

  .hero-line1,
  .hero-line2 {
    font-size: 6rem;
  }
}

@media (min-width: 1280px) {
  .hero-line1,
  .hero-line2 {
    font-size: 8rem;
  }

  .cta-button {
    padding: 1rem 2.5rem;
  }
}

@media (min-width: 1536px) {
  .hero-line1,
  .hero-line2 {
    font-size: 9rem;
  }
}
</style>