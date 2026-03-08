from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse

from .models import AgentRun, Author, Comment, HobbyTag, Image, Post, PostAgentMeta, TopicCandidate
from .services.discussion_agent import run_agent_once

"""
This module allows us to manipulate our database using the Django Admin panel.
"""

models_class = [Author, Post, Image, Comment, HobbyTag, TopicCandidate, PostAgentMeta]
for model in models_class:
    admin.site.register(model)


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display = ("started_at", "finished_at", "items_fetched", "items_kepts", "posts_created")
    ordering = ("-started_at",)
    change_list_template = "admin/soup/agentrun/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("run-agent/", self.admin_site.admin_view(self.run_agent_view), name="soup_agentrun_run"),
            path("dry-run-agent/", self.admin_site.admin_view(self.dry_run_agent_view), name="soup_agentrun_dry_run"),
        ]
        return custom_urls + urls

    def _changelist_url(self):
        opts = self.model._meta
        return reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")

    def run_agent_view(self, request):
        try:
            run = run_agent_once(dry_run=False)
            self.message_user(
                request,
                f"Agent completed: fetched={run.items_fetched}, kept={run.items_kepts}, created={run.posts_created}",
                level=messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(request, f"Agent run failed: {exc}", level=messages.ERROR)
        return HttpResponseRedirect(self._changelist_url())

    def dry_run_agent_view(self, request):
        try:
            run = run_agent_once(dry_run=True)
            self.message_user(
                request,
                f"Dry run completed: fetched={run.items_fetched}, kept={run.items_kepts}, created={run.posts_created}",
                level=messages.INFO,
            )
        except Exception as exc:
            self.message_user(request, f"Dry run failed: {exc}", level=messages.ERROR)
        return HttpResponseRedirect(self._changelist_url())
