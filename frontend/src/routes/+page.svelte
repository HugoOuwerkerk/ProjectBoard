<script lang="ts">
  import { onMount } from "svelte";
  import Modal from "$lib/components/Modal.svelte";

  let projects: any[] = [];
  let showModal = false;

  async function getProjects() {
    const res = await fetch("http://127.0.0.1:8000/getProjects");
    return await res.json();
  }

  function openModal() {
    showModal = true;
  }

  function addProject(e: SubmitEvent) {
    const formData = new FormData(e.target as HTMLFormElement);
    // formdata.get()
    showModal = false;
  }

  onMount(async () => {
    projects = await getProjects();
  });
</script>

<main class="landing">
  <header class="header">
    <h1>ProjectBoard</h1>
    <p>Organiseer je projecten, notities en taken op één plek.</p>
  </header>

  <!-- PROJECTS SECTION -->
  <section class="projects-wrap">
    <div class="projects-header">
      <h2>My Projects</h2>

      <!-- UI-ONLY controls (geen scripts, jij koppelt later) -->
      <form class="controls" aria-label="project controls">
        <label class="search">
          <svg viewBox="0 0 24 24" aria-hidden="true"
            ><path
              d="M21 21l-4.35-4.35m1.18-4.83a6 6 0 11-12 0 6 6 0 0112 0z"
            /></svg
          >
          <input type="search" placeholder="Zoek project..." />
        </label>
        <select class="filter" aria-label="filter">
          <option value="all">ALL</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="done">Done</option>
        </select>
        <button
          type="button"
          class="btn primary"
          aria-haspopup="dialog"
          on:click={() => (showModal = true)}>+ New Project</button
        >
      </form>
    </div>

    <!-- GRID -->
    <div class="projects">
      {#each projects as project}
        <article class="project-card">
          <header>
            <h3>{project.title}</h3>
            <span class="badge {project.status}">{project.status}</span>
          </header>
          <p class="desc">{project.description}</p>
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
        on:click={() => (showModal = true)}
        aria-haspopup="dialog"
        aria-label="Add a new project"
      >
        <div class="add-inner">
          <span class="plus">+</span>
          <p>New project</p>
        </div>
      </button>
    </div>
  </section>

  <Modal bind:open={showModal} title="Add new project" width="min(900px, 96vw)">
    <form
      class="modal-form"
      on:submit|preventDefault={addProject}
      aria-label="New project form"
    >
      <!-- Title -->
      <label class="field">
        <span class="label">Title <sup>*</sup></span>
        <input
          class="input"
          type="text"
          name="title"
          placeholder="e.g. ProjectBoard"
          required
          maxlength="80"
          autofocus
        />
        <small class="hint"
          >Short, clear project title (max 80 characters).</small
        >
      </label>

      <!-- Short description -->
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

      <!-- Description -->
      <label class="field">
        <span class="label">Description</span>
        <textarea
          class="textarea"
          name="description"
          rows="8"
          placeholder="What does this project do? What do you want to build?"
        ></textarea>
      </label>

      <!-- Links -->
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

      <!-- Status -->
      <label class="field">
        <span class="label">Status</span>
        <select class="select" name="status">
          <option value="idea" selected>Idea</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="done">Done</option>
        </select>
      </label>

      <!-- Footer actions go in the modal's footer slot so they right-align perfectly -->
      <div class="actions">
        <button
          type="button"
          class="btn ghost"
          on:click={() => (showModal = false)}>Cancel</button
        >
        <button type="submit" class="btn primary">Save</button>
      </div>
    </form>
  </Modal>
</main>

<style>
  /* ===== Global / Theme ===== */
  @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap");

  :global(html, body) {
    height: 100%;
    margin: 0;
    background: #0f1216; /* --bg */
    color: #eef1f4;
    font-family:
      "Inter",
      system-ui,
      -apple-system,
      Segoe UI,
      Roboto,
      Ubuntu,
      Cantarell,
      "Helvetica Neue",
      Arial;
  }
  :global(*),
  :global(*::before),
  :global(*::after) {
    box-sizing: border-box;
  }

  :root {
    /* Base theme */
    --bg: #0f1216;
    --text: #eef1f4;
    --muted: #9aa3ad;

    /* Panels & shadows */
    --panel: #151a21;
    --panel-border: rgba(255, 255, 255, 0.06);
    --shadow-1: 0 10px 30px rgba(0, 0, 0, 0.45);

    /* Buttons & borders */
    --btn: #2a313a;
    --btn-hover: #343c46;
    --stroke: rgba(255, 255, 255, 0.08);

    /* Cards (project grid) */
    --card: #1f242b;
    --card-hover: #262c34;

    /* Form fields */
    --field: #1b2027;
    --field-border: rgba(255, 255, 255, 0.12);
    --field-border-focus: rgba(155, 231, 187, 0.45);
    --primary: #50c878;
  }

  /* ===== Page ===== */
  .landing {
    min-height: 100dvh;
    background: var(--bg);
    color: var(--text);
    padding: 48px 20px 88px;
    display: grid;
    gap: 22px;
    place-items: center;
  }

  /* header */
  .header {
    text-align: center;
    margin-bottom: 8px;
  }
  .header h1 {
    font-size: clamp(36px, 6vw, 64px);
    line-height: 1.05;
    letter-spacing: -0.02em;
    font-weight: 800;
    text-shadow: 0 2px 20px rgba(0, 0, 0, 0.4);
    margin: 0;
  }
  .header p {
    margin-top: 8px;
    font-size: clamp(15px, 2vw, 20px);
    color: var(--muted);
  }

  /* ===== Projects wrapper ===== */
  .projects-wrap {
    width: min(1100px, 96vw);
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 20px;
    padding: 18px 18px 22px;
    box-shadow: var(--shadow-1);
  }
  .projects-header {
    display: flex;
    gap: 14px;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }
  .projects-header h2 {
    font-size: 18px;
    margin: 0;
  }
  .controls {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  /* Search + filter + button */
  .search {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--btn);
    border: 1px solid var(--stroke);
    padding: 6px 10px;
    border-radius: 10px;
  }
  .search svg {
    width: 16px;
    height: 16px;
    fill: none;
    stroke: #9aa3ad;
    stroke-width: 2;
  }
  .search input {
    background: transparent;
    border: 0;
    color: var(--text);
    outline: none;
    min-width: 180px;
  }
  .filter {
    background: var(--btn);
    border: 1px solid var(--stroke);
    color: var(--text);
    padding: 6px 10px;
    border-radius: 10px;
  }
  .btn {
    background: var(--btn);
    border: 1px solid var(--stroke);
    color: var(--text);
    padding: 8px 12px;
    border-radius: 10px;
    cursor: pointer;
    transition:
      background 0.15s ease,
      border-color 0.15s ease,
      transform 0.06s ease;
  }
  .btn.primary {
    border-color: rgba(80, 200, 120, 0.25);
  }
  .btn:hover {
    background: var(--btn-hover);
  }
  .btn:active {
    transform: translateY(1px);
  }
  .btn.ghost {
    background: transparent;
  }

  /* ===== Projects grid ===== */
  .projects {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }
  .project-card {
    background: var(--card);
    color: var(--text);
    border: 1px solid var(--panel-border);
    border-radius: 14px;
    padding: 14px;
    transition:
      background 0.15s ease,
      transform 0.06s ease;
  }
  .project-card:hover {
    background: var(--card-hover);
    transform: translateY(-1px);
  }
  .project-card header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .project-card h3 {
    font-size: 16px;
    margin: 0;
  }

  /* Status badges */
  .badge {
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 999px;
    border: 1px solid var(--panel-border);
    background: #1c2420;
    text-transform: capitalize;
  }
  .badge.idea {
    color: #c7f9cc;
    border-color: rgba(120, 220, 160, 0.35);
  }
  .badge.active {
    color: #9be7bb;
    border-color: rgba(80, 200, 120, 0.35);
  }
  .badge.paused {
    color: #e7d4ae;
    border-color: rgba(191, 161, 129, 0.35);
  }
  .badge.done {
    color: #a0c4ff;
    border-color: rgba(160, 196, 255, 0.35);
  }

  .desc {
    color: var(--muted);
    font-size: 14px;
    margin: 6px 0 10px;
  }
  .meta {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    padding: 0;
    margin: 0 0 10px;
    list-style: none;
  }
  .meta li {
    font-size: 12px;
    color: #c5cbd3;
    background: #141920;
    padding: 4px 8px;
    border-radius: 8px;
  }
  .project-card footer .link {
    color: #cfe9da;
    text-decoration: none;
    font-weight: 600;
  }

  /* Add card */
  .add-card {
    border: 1px dashed rgba(255, 255, 255, 0.15);
    background: transparent;
    display: grid;
    place-items: center;
    min-height: 140px;
  }
  .add-inner {
    text-align: center;
    color: #cbd5df;
  }
  .add-inner .plus {
    display: inline-grid;
    place-items: center;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: #1f2730;
    border: 1px solid var(--stroke);
    margin-bottom: 8px;
    font-size: 22px;
    line-height: 1;
  }

  /* ===== Modal: panel & layout are handled in the component.
     Only keep the form field styles here so everything lines up. ===== */

  .modal-form {
    width: 100%;
  } /* the <form> inside Modal slot */

  .field {
    display: grid;
    gap: 8px;
    margin: 14px 0;
  }
  .label {
    font-size: 13px;
    color: var(--muted);
  }
  .label sup {
    color: #eab308;
    top: -0.2em;
    position: relative;
  }

  .input,
  .textarea,
  .select {
    width: 100%;
    background: var(--field);
    color: var(--text);
    border: 1px solid var(--field-border);
    border-radius: 12px;
    padding: 12px 14px;
    font: inherit;
    outline: none;
    transition:
      border-color 0.15s ease,
      box-shadow 0.15s ease,
      background 0.15s ease;
    box-sizing: border-box; /* prevents right-edge overflow */
  }
  .input::placeholder,
  .textarea::placeholder {
    color: rgba(238, 241, 244, 0.45);
  }
  .input:focus,
  .textarea:focus,
  .select:focus {
    border-color: var(--field-border-focus);
    box-shadow: 0 0 0 4px rgba(80, 200, 120, 0.15);
  }
  .textarea {
    resize: vertical;
    min-height: 200px;
  }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }
  .hint {
    font-size: 12px;
    color: var(--muted);
  }

  .actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }

  /* ===== Responsive ===== */
  @media (max-width: 980px) {
    .projects {
      grid-template-columns: 1fr 1fr;
    }
  }
  @media (max-width: 680px) {
    .projects {
      grid-template-columns: 1fr;
    }
    .projects-header {
      flex-direction: column;
      align-items: stretch;
      gap: 8px;
    }
    .controls {
      width: 100%;
    }
    .search {
      flex: 1;
    }
    .grid-2 {
      grid-template-columns: 1fr;
    }
  }
</style>
