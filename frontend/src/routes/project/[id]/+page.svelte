<script lang="ts">
  import { page } from '$app/stores';
  import Modal from '$lib/components/Modal.svelte';
  import { onMount } from 'svelte';

  const columns = [
    { key: 'open', label: 'Open', empty: 'No open tasks', class: '' },
    { key: 'in_progress', label: 'In Progress', empty: 'No tasks in progress', class: 'col-mid' },
    { key: 'done', label: 'Done', empty: 'Everything is done 🎉', class: 'col-done' }
  ];

  let project = $state<any>(null);
  let projectId = $derived($page.params.id);

  let showAddTask = $state(false);
  let showEditProject = $state(false);
  let showAddNote = $state(false);
  let showEditNote = $state(false);

  async function getProject() {
    const res = await fetch(`http://127.0.0.1:8000/getProject/${projectId}`);
    project = await res.json();
  }

  async function addTask(e: SubmitEvent) {
    e.preventDefault();
    const form = e.currentTarget as HTMLFormElement;
    const formData = new FormData(form);

    //needs change(easyer way, changes in api mayby or in the ui)
    let rawLabels = formData.get("labels");
    let labels: string[] = []; 
    if (rawLabels) {
      labels = rawLabels
        .toString()
        .split(",")
        .map(l => l.trim())
        .filter(l => l.length > 0);
    }

    const payload = {
      title: formData.get("title"),
      desc: formData.get("description"),
      labels: labels
    };

    const res = await fetch(`http://127.0.0.1:8000/projects/${projectId}/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    project = await res.json();
    showAddTask = false;
  }

  async function deleteTask(taskId: number) {
    await fetch(`http://127.0.0.1:8000/projects/${projectId}/tasks/${taskId}`, {
      method: "DELETE"
    });
    await getProject();
  }
  // not added yet
  async function updateTaskStatus(taskId: number, newStatus: string) {
    await fetch(`http://127.0.0.1:8000/projects/${projectId}/tasks/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    await getProject();
  }

  async function editProject(e: SubmitEvent) {
    e.preventDefault();
    const form = e.currentTarget as HTMLFormElement;
    const formData = new FormData(form);

    const payload = {
      title: formData.get("title"),
      short_description: formData.get("short_description"),
      description: formData.get("description"),
      github: formData.get("github"),
      website: formData.get("website"),
      status: formData.get("status")
    };

    const res = await fetch(`http://127.0.0.1:8000/projects/${projectId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    project = await res.json();
    showEditProject = false;
  }

  async function addNote(e: SubmitEvent) {
    e.preventDefault();
    const form = e.currentTarget as HTMLFormElement;
    const formData = new FormData(form);

    const payload = {
      desc: formData.get("note")
    };

    const res = await fetch(`http://127.0.0.1:8000/projects/${projectId}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    await getProject();
    showAddNote = false;

  }

  async function deleteNote(noteId: number) {
    await fetch(`http://127.0.0.1:8000/projects/${projectId}/notes/${noteId}`, {
      method: "DELETE"
    });
    await getProject();
  }

  async function editNote(e: SubmitEvent, noteId: number) {
    e.preventDefault();
    const form = e.currentTarget as HTMLFormElement;
    const formData = new FormData(form);

    const payload = {
      desc: formData.get("note"),

    };

    const res = await fetch(`http://127.0.0.1:8000/projects/${projectId}/notes/${noteId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    await getProject();
    showEditNote = false;
  }

  onMount(async () => {
    await getProject();
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
        {#each project.notes as note, id}
          <li>
            {note.desc}
            <button class="btn small" title="Edit note" onclick={() => {/* implement edit logic */}}>Edit</button>
            <button class="btn small" title="delete note" onclick={() => {deleteNote(note.id)}}>delete</button>
          </li>
        {/each}
      </ul>
      <button class="btn small" onclick={() => (showAddNote = true)}>Add note</button>
    </aside>

    <div class="details-actions">
      <button class="btn small_edit" data-action="edit-details" onclick={() => (showEditProject = true)}>Edit</button>
    </div>
  </section>

  <!-- board section -->
  <section class="board">
    {#each columns as col}
      <div class="col {col.class}">
        <div class="col-header">
          <h2>{col.label} <span class="count">({project[col.key]?.length || 0})</span></h2>
          {#if col.key === 'open'}
            <button class="btn small" onclick={() => (showAddTask = true)}>
              <svg viewBox="0 0 24 24" class="icon"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" fill="none"/></svg>
              Add task
            </button>
          {/if}
        </div>
        {#if project[col.key] && project[col.key].length}
          {#each project[col.key] as task (task.id || task.title)}
            <div class="card">
              <span class="chip"></span>
              <h3 class="task-title">{task.title}</h3>
              {#if task.desc}<p class="task-desc">{task.desc}</p>{/if}
              {#if task.labels?.length}
                <div class="labels">
                  {#each task.labels as label}<span class="label">{label.name ?? label}</span>{/each}
                </div>
              {/if}
              <button class="btn delete-task" title="Delete task" onclick={() => (deleteTask(task.id))}>🗑️</button>
            </div>
          {/each}
        {:else}
          <div class="empty">{col.empty}</div>
        {/if}
      </div>
    {/each}
  </section>



 <!-- add task modal -->
  <Modal bind:open={showAddTask} title="Add task">
    <form class="modal-form" onsubmit={addTask}>
      <label class="field">
        <span class="label">Title <sup>*</sup></span>
        <input class="input" type="text" placeholder="e.g. Fix login bug" required maxlength="100" name="title"/>
      </label>

      <label class="field">
        <span class="label">Description</span>
        <textarea class="textarea" rows="6" placeholder="Details about what needs to be done" name="description"></textarea>
      </label>

      <label class="field">
        <span class="label">Labels (comma separated)</span>
        <input class="input" type="text" placeholder="e.g. bug, backend, urgent" name="labels"/>
      </label>

      <div class="actions">
        <button type="button" class="btn ghost" onclick={() => (showAddTask = false)}>Cancel</button>
        <button type="submit" class="btn primary">Add</button>
      </div>
    </form>
  </Modal>

   <!-- edit project modal -->
  <Modal bind:open={showEditProject} title="Add a new project">
    <form class="modal-form" onsubmit={editProject} aria-label="New project form">
      <label class="field">
        <span class="label">Title <sup>*</sup></span>
        <input class="input" type="text" name="title" value="{project.title}" required maxlength="80"/>
      </label>

      <label class="field">
        <span class="label">Short description</span>
        <input class="input" type="text" name="short_description" value="{project.short_description}" maxlength="140"/>
      </label>

      <label class="field">
        <span class="label">Description</span>
        <textarea class="textarea" name="description" rows="8" value="{project.description}"></textarea>
      </label>

      <div class="grid-2">
        <label class="field">
          <span class="label">GitHub (optional)</span>
          <input class="input" type="url" name="github" value="{project.github}"/>
        </label>

        <label class="field">
          <span class="label">Website (optional)</span>
          <input class="input" type="url" name="website" value="{project.website}"/>
        </label>
      </div>

      <label class="field">
        <span class="label">Status</span>
        <select class="select" name="status" bind:value={project.status}>
          <option value="idea">Idea</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="done">Done</option>
        </select>
      </label>

      <div class="actions">
        <button type="button" class="btn ghost" onclick={() => (showEditProject = false)}>Cancel</button>
        <button type="submit" class="btn primary">Save</button>
      </div>
    </form>
  </Modal>

  <!-- add note modal -->
  <Modal bind:open={showAddNote} title="Add note">
    <form class="modal-form" onsubmit={addNote}>
      <label class="field">
        <span class="label">Note</span>
        <textarea class="textarea" name="note" rows="4" required></textarea>
      </label>
      <div class="actions">
        <button type="button" class="btn ghost" onclick={() => { showAddNote = false}}>Cancel</button>
        <button type="submit" class="btn primary">Add</button>
      </div>
    </form>
  </Modal>

</main>
{:else}
  <p>Project not found</p>
{/if}





