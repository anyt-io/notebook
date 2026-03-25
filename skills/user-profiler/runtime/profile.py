"""CLI entry point for user-profiler skill."""

import argparse
import json
import os
import sys
from dataclasses import asdict

from profile_manager import ProfileManager
from recommender import Recommender
from trend_analyzer import TrendAnalyzer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="User Profiler - Track interview performance and generate recommendations"
    )
    parser.add_argument("--user-id", required=True, help="Unique user identifier")
    parser.add_argument("--session", type=str, default=None, help="Path to session results JSON file")
    parser.add_argument("--recommend", action="store_true", help="Generate training recommendations")
    parser.add_argument("--summary", action="store_true", help="Show profile summary")
    parser.add_argument("--output", type=str, default="output/", help="Output directory (default: output/)")

    args = parser.parse_args()

    # Use output dir as storage for profiles too
    os.makedirs(args.output, exist_ok=True)
    manager = ProfileManager(args.output)
    profile = manager.load_profile(args.user_id)

    if args.session:
        # Add session mode
        if not os.path.exists(args.session):
            print(f"Error: session file not found: {args.session}", file=sys.stderr)
            sys.exit(1)
        with open(args.session) as f:
            session_data = json.load(f)
        profile = manager.add_session(profile, session_data)
        manager.save_profile(profile)
        print(f"Session added. Total sessions: {profile.total_sessions}")
        print(f"Latest score: {profile.latest_score:.2f} | Best score: {profile.best_score:.2f}")

        # Also save a user_profile.json for convenience
        profile_out = os.path.join(args.output, "user_profile.json")
        with open(profile_out, "w") as f:
            json.dump(asdict(profile), f, indent=2)
        print(f"Profile saved to {profile_out}")

    if args.recommend:
        # Generate recommendations
        recommendations = Recommender.generate_recommendations(profile)
        rec_out = os.path.join(args.output, "recommendations.json")
        with open(rec_out, "w") as f:
            json.dump([asdict(r) for r in recommendations], f, indent=2)
        print(f"\nGenerated {len(recommendations)} recommendations -> {rec_out}")
        for rec in recommendations:
            print(f"  [{rec.priority.upper()}] {rec.category}: {rec.description}")

        # Also generate progress report
        report = TrendAnalyzer.generate_progress_report(profile)
        report_out = os.path.join(args.output, "progress_report.json")
        with open(report_out, "w") as f:
            json.dump(asdict(report), f, indent=2)
        print(f"Progress report saved to {report_out}")

    if args.summary:
        # Show summary
        print(f"\n=== Profile Summary: {profile.user_id} ===")
        print(f"Created: {profile.created_at}")
        print(f"Total sessions: {profile.total_sessions}")
        print(f"Best score: {profile.best_score:.2f}")
        print(f"Latest score: {profile.latest_score:.2f}")
        print(f"Overall trend: {profile.overall_trend}")
        if profile.category_trends:
            print("\nCategory Trends:")
            for cat, trend in profile.category_trends.items():
                latest = trend.scores[-1] if trend.scores else 0.0
                print(f"  {cat}: {latest:.2f} ({trend.trend_direction}, rate={trend.improvement_rate:+.3f})")
        weak = TrendAnalyzer.identify_weak_areas(profile)
        strong = TrendAnalyzer.identify_strong_areas(profile)
        if weak:
            print(f"\nWeak areas: {', '.join(weak)}")
        if strong:
            print(f"Strong areas: {', '.join(strong)}")

    if not args.session and not args.recommend and not args.summary:
        parser.print_help()


if __name__ == "__main__":
    main()
