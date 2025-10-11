---
permalink: /projects/
title: Projekte
archiver_repo_url: "" # Optional: set your URL-Archiver GitHub repo here
---

{% comment %}
Bachelor-Thesis aus den CV-Daten beziehen und hier darstellen.
Bitte die GitHub-Repo-URL unten ergänzen und die PDF der Thesis unter
assets/files/bachelor_thesis_nicolin_dora.pdf ablegen (oder den Namen anpassen).
{% endcomment %}

{% assign thesis = site.data.cv.sections.projects.items | where: "name", "Digital und sicher: Neue Wege für die Schulkommunikation" | first %}
{% if thesis %}
<section class="project">
	<h2>{{ thesis.name }}</h2>
	<p class="project-meta">{{ thesis.description }} · {{ thesis.date }}</p>
	<div class="project-summary">{{ thesis.summary }}</div>
	<p>
		<a href="https://github.com/devobern/BFH-Bachelorarbeit-Proof-of-Concept" target="_blank" rel="noopener">Proof of Concept (GitHub)</a>
		·
		<a href="{{ '/assets/files/Digital_und_sicher_Neue_Wege_für_die_Schulkommunikation.pdf' | relative_url }}" download>PDF herunterladen</a>
	</p>
</section>
{% endif %}

{% assign archiver = site.data.cv.sections.projects.items | where: "name", "URL-Archiver" | first %}
{% if archiver %}
<section class="project">
	<h2>{{ archiver.name }}</h2>
	<p class="project-meta">{{ archiver.description }} · {{ archiver.date }}</p>
	<div class="project-summary">{{ archiver.summary }}</div>
	<p>
		<a href="{{ page.archiver_repo_url | default: 'https://github.com/devobern/URL-Archiver' }}" target="_blank" rel="noopener">GitHub‑Repository</a>
	</p>
</section>
{% endif %}