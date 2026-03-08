from django.core.management.base import BaseCommand
from Soup.services.discussion_agent import run_agent_once


class Command(BaseCommand):
    help = "Run AI discussion agent pipeline"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--external-cap", type=int, default=2)
        parser.add_argument("--revival-cap", type=int, default=1)

    def handle(self, *args, **options):
        run = run_agent_once(
            dry_run=options["dry_run"],
            external_cap=options["external_cap"],
            revival_cap=options["revival_cap"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Agent run complete: fetched={run.items_fetched}, kept={run.items_kepts}, created={run.posts_created}"
            )
        )
