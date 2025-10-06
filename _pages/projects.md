---
permalink: /projects/
title: Projekte
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
	<p style="color: var(--muted); margin-top: -.5rem;">{{ thesis.description }} · {{ thesis.date }}</p>
	<div class="project-summary">{{ thesis.summary }}</div>
	<p>
		<!-- TODO: Ersetze REPO_NAME mit dem tatsächlichen Repository-Namen -->
		<a href="https://github.com/devobern/BFH-Bachelorarbeit-Proof-of-Concept" target="_blank" rel="noopener">Proof of Concept (GitHub)</a>
		·
		<a href="{{ '/assets/files/Digital_und_sicher_Neue_Wege_für_die_Schulkommunikation.pdf' | relative_url }}" download>PDF herunterladen</a>
	</p>
</section>
{% endif %}