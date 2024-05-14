'use client'

export default function myImageLoader({ src, width, quality }) {
  return `localhost:8000/api/users/file-assets/${src}?w=${width}&q=${quality || 75}`
}