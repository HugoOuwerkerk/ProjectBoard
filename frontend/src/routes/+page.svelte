<script lang="ts">
  import { onMount } from "svelte";
  import Modal from "$lib/components/Modal.svelte";
  
  let search = $state("");
  let statusFilter = $state("all");
  let allProjects = $state<any[]>([])
  let showAddProject = $state(false);

  let filteredProjects = $derived.by(() => {
    const searchTerm = (search ?? "").toLowerCase();

    return allProjects.filter(project => {
      const matchesTitle = !searchTerm || project.title.toLowerCase().includes(searchTerm)
;

      const matchesStatus = statusFilter === "all" || project.status === statusFilter;

      return matchesTitle && matchesStatus;
    });
  });

  async function getProjects() {
    const res = await fetch("http://127.0.0.1:8000/getProjects");
    return await res.json();
  }

  async function addProject(event: SubmitEvent) {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement;
    const formData = new FormData(form);

    const payload = {
      title: formData.get("title"),
      short_description: formData.get("short_description"),
      description: formData.get("description"),
      github: formData.get("github"),
      website: formData.get("website"),
      status: formData.get("status")
    };

    const res = await fetch("http://127.0.0.1:8000/addProject/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      console.error("addProject failed", await res.text());
      return;
    }

    const data = await res.json();

    allProjects = [...allProjects, data];

    showAddProject = false;
    form.reset();
  }


  onMount(async () => {
    allProjects = await getProjects();
  });
</script>

<main class="landing">
  <header class="header">
    <h1>ProjectBoard</h1>
    <p>Organiseer je projecten, notities en taken op één plek.</p>
  </header>

  <!-- projects section -->
  <section class="projects-wrap">
    <div class="projects-header">
      <h2>My Projects</h2>

      <form class="controls" aria-label="project controls">
        <label class="search">
          <svg viewBox="0 0 24 24" aria-hidden="true"
            ><path
              d="M21 21l-4.35-4.35m1.18-4.83a6 6 0 11-12 0 6 6 0 0112 0z"
            /></svg
          >
          <input type="search" placeholder="Zoek project..." bind:value={search}/>
        </label>
          <select class="filter" aria-label="filter" bind:value={statusFilter}>
            <option value="all">ALL</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="done">Done</option>
            <option value="idea">Idea</option>
          </select>
        <button
          type="button"
          class="btn primary"
          aria-haspopup="dialog"
          onclick={() => (showAddProject = true)}>+ New Project</button
          
        >
      </form>
    </div>

    <!-- grid -->
    <div class="projects">
      {#each filteredProjects as project}
        <article class="project-card">
          <header>
            <h3>{project.title}</h3>
            <span class="badge {project.status}">{project.status}</span>
          </header>
          <p class="desc">{project.short_description}</p>
          <ul class="meta">
            <li>{project.open.length} open taken</li>
            <li>{project.in_progress.length} in progress</li>
            <li>{project.done.length} done</li>
          </ul>
          <footer>
            <a
              class="link"
              href="/project/{project.id}"
              aria-label="Open project">Openen →</a
            >
          </footer>
        </article>
      {/each}

      <button
        type="button"
        class="project-card add-card"
        onclick={() => (showAddProject = true)}
        aria-haspopup="dialog"
      >
        <div class="add-inner">
          <span class="plus">+</span>
          <p>New project</p>
        </div>
      </button>
    </div>
  </section>

  <!-- add project modal -->
  <Modal bind:open={showAddProject} title="Add a new project">
    <form
      class="modal-form"
      onsubmit={addProject}
      aria-label="New project form"
    >
      <label class="field">
        <span class="label">Title <sup>*</sup></span>
        <!-- svelte-ignore a11y_autofocus -->
        <input
          class="input"
          type="text"
          name="title"
          placeholder="e.g. ProjectBoard"
          required
          maxlength="80"
          autofocus
        />
      </label>

      <label class="field">
        <span class="label">Short description</span>
        <input
          class="input"
          type="text"
          name="short_description"
          placeholder="One sentence about the project"
          maxlength="140"
        />
      </label>

      <label class="field">
        <span class="label">Description</span>
        <textarea
          class="textarea"
          name="description"
          rows="8"
          placeholder="What does this project do? What do you want to build?"
        ></textarea>
      </label>

      <div class="grid-2">
        <label class="field">
          <span class="label">GitHub (optional)</span>
          <input
            class="input"
            type="url"
            name="github"
            placeholder="https://github.com/..."
          />
        </label>

        <label class="field">
          <span class="label">Website (optional)</span>
          <input
            class="input"
            type="url"
            name="website"
            placeholder="https://..."
          />
        </label>
      </div>

      <label class="field">
        <span class="label">Status</span>
        <select class="select" name="status">
          <option value="idea" selected>Idea</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="done">Done</option>
        </select>
      </label>

      <div class="actions">
        <button
          type="button"
          class="btn ghost"
          onclick={() => (showAddProject = false)}>Cancel</button
        >
        <button type="submit" class="btn primary">Save</button>
      </div>
    </form>
  </Modal>
</main>
