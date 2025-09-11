<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  let project = $state<any>(null);
  let projectId = $derived($page.params.id);

  async function getProject() {
    const res = await fetch(`http://127.0.0.1:8000/getProject/${projectId}`);
    if (!res.ok) {
    return null;
    }
    return await res.json();
  }

  async function addTask() {
    const payload = {
      title: "Test Task",
      desc: "This is just a test task",
      labels: ["feature", "ui"]
    };

    const res = await fetch("http://127.0.0.1:8000/projects/1/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    project = data;
    console.log("Updated project:", data);
  }

  async function deleteTask() {
    
  }

  async function updateTask() {
    
  }

  async function editProject() {
    
  }

  onMount(async () => {
    project = await getProject();
  });
</script>

<svelte:head>
  <title>{project ? `${project.title} – ProjectBoard` : 'ProjectBoard'}</title>
</svelte:head>


{#if project}
<main class="project-page">
  <nav class="page-actions">
    <a href="/" class="btn back-btn" aria-label="Go back" data-action="back">
      <svg viewBox="0 0 24 24" aria-hidden="true" class="icon"><path d="M15 18l-6-6 6-6" fill="none" stroke="currentColor" stroke-width="2"/></svg>
      Back
    </a>
  </nav>
  <header class="header">
    <h1>{project.title}</h1>
    <p>{project.short_description}</p>
  </header>

  <!-- DETAILS -->
  <section class="project-details">
    <div class="info">
      <h2>Description</h2>
      <p>{project.description}</p>

      <div class="links">
        {#if project.github}
        <a class="btn" href="{project.github}" target="_blank">GitHub →</a>
        {/if}
        {#if project.website}
        <a class="btn" href="{project.website}" target="_blank">Website →</a>
        {/if}
      </div>
    </div>

    <aside class="notes">
      <h2>Notes</h2>
      <ul>
        {#each project.notes as note}
        <li>{note.desc}</li>
        {/each}
      </ul>        
    </aside>

    <div class="details-actions">
      <button class="btn small_edit" data-action="edit-details" onclick={() => (editProject())}>Edit</button>
    </div>
  </section>

<section class="board">
  <div class="col">
    <div class="col-header">
      <h2>Open <span class="count">({project.open?.length || 0})</span></h2>
      <button class="btn small" aria-label="Add open task" data-action="add-task" data-status="open" onclick={() => (addTask())}>
        <svg viewBox="0 0 24 24" class="icon">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        Add task
      </button>
    </div>

    {#if project.open && project.open.length}
      {#each project.open as task}
        <div class="card">
          <span class="chip"></span>

          {#if typeof task === 'string'}
            <h3 class="task-title">{task}</h3>
          {:else}
            <h3 class="task-title">{task.title}</h3>
            {#if task.desc}<p class="task-desc">{task.desc}</p>{/if}
            {#if task.labels}
              <div class="labels">
                {#each task.labels as label}<span class="label">{label.name}</span>{/each}
              </div>
            {/if}
          {/if}
        </div>
      {/each}
    {:else}
      <div class="empty">No open tasks</div>
    {/if}
  </div>

  <div class="col col-mid">
    <h2>In Progress <span class="count">({project.in_progress?.length || 0})</span></h2>

    {#if project.in_progress && project.in_progress.length}
      {#each project.in_progress as task}
        <div class="card">
          <span class="chip"></span>

          {#if typeof task === 'string'}
            <h3 class="task-title">{task}</h3>
          {:else}
            <h3 class="task-title">{task.title}</h3>
            {#if task.desc}<p class="task-desc">{task.desc}</p>{/if}
            {#if task.labels}
              <div class="labels">
                {#each task.labels as label}<span class="label">{label.name}</span>{/each}
              </div>
            {/if}
          {/if}
        </div>
      {/each}
    {:else}
      <div class="empty">No tasks in progress</div>
    {/if}
  </div>

  <div class="col col-done">
    <h2>Done <span class="count">({project.done?.length || 0})</span></h2>

    {#if project.done && project.done.length}
      {#each project.done as task}
        <div class="card">
          <span class="chip"></span>

          {#if typeof task === 'string'}
            <h3 class="task-title">{task}</h3>
          {:else}
            <h3 class="task-title">{task.title}</h3>
            {#if task.desc}<p class="task-desc">{task.desc}</p>{/if}
            {#if task.labels}
              <div class="labels">
                {#each task.labels as label}<span class="label">{label.name}</span>{/each}
              </div>
            {/if}
          {/if}
        </div>
      {/each}
    {:else}
      <div class="empty">Everything is done 🎉</div>
    {/if}
  </div>
</section>


</main>
{:else}
  <p>Project not found</p>
{/if}

<style>
  /* Font + global reset (prevents white border) */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

  :global(html, body) {
    height: 100%;
    margin: 0;
    background: #0f1216; /* matches --bg */
    color: #eef1f4;
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial;
  }
  :global(*), :global(*::before), :global(*::after) { box-sizing: border-box; }

  :root {
    --bg: #0f1216;
    --text: #eef1f4;
    --muted: #9aa3ad;

    --panel: #151a21;
    --panel-border: rgba(255, 255, 255, 0.06);
    --shadow-1: 0 10px 30px rgba(0, 0, 0, 0.45);
    --shadow-2: 0 2px 6px rgba(0, 0, 0, 0.25);

    /* Column backgrounds */
    --col-left: #1e232b;
    --col-mid:  #202736;
    --col-done: #1e2a24;

    /* Card backgrounds (DARK so text is readable) */
    --card-left: #1f242b;
    --card-mid:  #232b36;
    --card-done: #1e2a24;

    /* Tiny chip tones */
    --chip-left: rgba(255,255,255,0.10);
    --chip-mid:  rgba(255,255,255,0.10);
    --chip-done: rgba(255,255,255,0.10);

    /* Buttons */
    --btn: #2a313a;
    --btn-hover: #343c46;

    /* Links */
    --link: #9be7bb;
    --link-hover: #b7f0cc;
  }
  
  .project-page {
    min-height: 100vh;
    background: var(--bg);
    color: var(--text);
    padding: 40px 20px 72px;
    display: grid;
    gap: 24px;
    place-items: center;
  }

    /* Back button */
  .page-actions {
    width: min(1000px, 95vw);
    display: flex;
    justify-content: flex-start;
  }
  .back-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
  }

  /* HEADER */
  .header { text-align: center; }
  .header h1 {
    font-size: clamp(36px, 6vw, 56px);
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0;
  }
  .header p {
    margin: 8px 0 0;
    font-size: clamp(15px, 2vw, 20px);
    color: var(--muted);
  }

  /* DETAILS */
  .project-details {
    width: min(1000px, 95vw);
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 16px;
    padding: 20px;
    box-shadow: var(--shadow-1);
    position: relative;
  }

  .details-actions {
  position: absolute;
  bottom: 12px;
  right: 16px;
  }
  .info h2, .notes h2 {
    font-size: 18px;
    margin: 0 0 10px;
  }
  .links {
    margin-top: 14px;
    display: flex;
    gap: 10px;
  }
  .btn {
    background: var(--btn);
    border: 1px solid var(--panel-border);
    color: var(--text);
    padding: 8px 14px;
    border-radius: 10px;
    text-decoration: none;
    transition: background 0.15s ease, border-color 0.15s ease;
  }
  .btn.small_edit {
    padding: 6px 10px;
    font-size: 13px;
    border-radius: 8px;
  }

  .icon { width: 16px; height: 16px; display: inline-block; }

  .btn:hover { background: var(--btn-hover); }
  .notes ul {
    list-style: disc;
    padding-left: 18px;
    color: var(--muted);
    font-size: 14px;
    margin: 0;
  }

  /* BOARD */
  .board {
    width: min(1000px, 95vw);
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 16px;
    padding: 20px;
    box-shadow: var(--shadow-1);
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  .col-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px; /* keeps spacing before tasks */
  }

  .col-header h2 {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
  }

  .btn.small {
    padding: 4px 8px;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .btn.small .icon {
    width: 14px;
    height: 14px;
  }

  .col {
    background: var(--col-left);
    border-radius: 14px;
    padding: 12px;
    box-shadow: var(--shadow-2) inset;
  }
  .col-mid { background: var(--col-mid); }
  .col-done { background: var(--col-done); }

  .col h2 {
    margin: 0 0 10px;
    font-size: 15px;
    font-weight: 700;
    color: #e7ebf0;
  }
  .count { color: var(--muted); font-weight: 600; font-size: .9em; }

  .card {
    border-radius: 12px;
    padding: 12px;
    margin: 10px 0;
    background: var(--card-left);
    color: var(--text);
    box-shadow:
      inset 0 1px 0 rgba(255,255,255,0.04),
      0 6px 18px rgba(0,0,0,0.35);
  }
  .col-mid .card { background: var(--card-mid); }
  .col-done .card { background: var(--card-done); }

  .chip {
    display: inline-block;
    height: 10px; width: 72px;
    border-radius: 999px;
    background: var(--chip-left);
    margin-bottom: 10px;
  }
  .col-mid .chip  { background: var(--chip-mid); }
  .col-done .chip { background: var(--chip-done); }

  .task-title { margin: 0 0 6px; font-weight: 700; font-size: 14px; }
  .task-desc  { margin: 0; font-size: 13px; color: var(--muted); }
  .labels { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
  .label  { font-size: 11px; padding: 2px 6px; border-radius: 6px; background: rgba(255,255,255,0.08); color: var(--muted); }

  .empty { font-size: 13px; color: var(--muted); padding: 8px 0; }

  /* Links */
  a { color: var(--link); text-decoration: none; }
  a:hover { color: var(--link-hover); }

  /* Responsive */
  @media (max-width: 900px) {
    .project-details { grid-template-columns: 1fr; }
  }
</style>



