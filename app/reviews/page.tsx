"use client"

import { useEffect, useState } from "react"
import { Star, MessageCircle, Sparkles } from "lucide-react"

type Review = { id: number; skill: string; rating: number; comment: string; author: string; date: string }

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<Review[]>([])

  useEffect(() => {
    fetch("/api/reviews").then(r => r.json()).then(setReviews)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur border-b border-border">
        <div className="container px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <MessageCircle className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-xl font-bold">Reviews</h1>
          </div>
        </div>
      </header>

      <main className="container px-4 py-8">
        <div className="space-y-4">
          {reviews.map((review, i) => (
            <div key={review.id} className="p-6 rounded-2xl bg-card border border-border animate-slide-up" style={{ animationDelay: `${i * 100}ms` }}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <span className="font-semibold text-lg">@{review.skill}</span>
                  <span className="text-muted-foreground text-sm ml-3">by {review.author}</span>
                </div>
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <Star key={s} className={`w-4 h-4 ${s <= review.rating ? "fill-yellow-400 text-yellow-400" : "text-gray-600"}`} />
                  ))}
                </div>
              </div>
              <p className="text-muted-foreground">{review.comment}</p>
              <p className="text-xs text-muted-foreground mt-3">{review.date}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
