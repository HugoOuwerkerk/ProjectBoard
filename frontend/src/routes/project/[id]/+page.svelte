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
  let loaded = $state(false);
  let loadError = $state<string | null>(null);

  let showAddTask = $state(false);
  let showEditProject = $state(false);
  let showAddNote = $state(false);

 async function getProject() {
   loadError = null;
   project = null;
   const id = $page.params.id;
   if (!id) { loaded = true; return; }
   try {
    const res = await fetch(`/api/getProject/${id}`);
     if (!res.ok) {
       loadError = `HTTP ${res.status}: ${await res.text()}`;
       project = null;
     } else {
       project = await res.json();
     }
   } catch (e: any) {
     loadError = e?.message ?? 'Network error';
     project = null;
   } finally {
     loaded = true;
   }
 }

 async function deleteProject() {
  const res = await fetch(`/api/projects/${project.id}`, {
    method: "DELETE"
  });

  if (res.ok) {
    window.location.href = "/";
  } else {
    alert("Failed to delete project");
  }
}

  async function addTask(e: SubmitEvent) {
    e.preventDefault();
    const form = e.currentTarget as HTMLFormElement;
    const formData = new FormData(form);

    let rawLabels = formData.get("labels");
    let labels: string[] = [];
    if (rawLabels) {
      labels = rawLabels
        .toString()
        .split(",")
        .map((l) => l.trim())
        .filter((l) => l.length > 0);
    }

    const payload = {
      title: formData.get("title"),
      desc: formData.get("description"),
      labels
    };

    const res = await fetch(`/api/projects/${project.id}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const created = await res.json();
    const colKey = created.status || "open";
    project[colKey] = [...(project[colKey] || []), created];

    showAddTask = false;
    form.reset();
  }

  async function deleteTask(taskId: number) {
    const res = await fetch(
      `/api/projects/${project.id}/tasks/${taskId}`,
      { method: "DELETE" }
    );

    if (res.ok) {
      for (const col of columns) {
        if (project[col.key]) {
          project[col.key] = project[col.key].filter((t: any) => t.id !== taskId);
        }
      }
    }
  }
  
  function findTaskColumn(taskId: number): string | null {
  for (const col of columns) {
    const list = project[col.key] || [];
    if (list.some((t: any) => t.id === taskId)) return col.key;
  }
  return null;
}

function patchDefined<T extends Record<string, any>>(base: T, partial: Partial<T>): T {
  const out = { ...base };
  for (const k in partial) {
    if (Object.prototype.hasOwnProperty.call(partial, k) && partial[k] !== undefined) {
      (out as any)[k] = partial[k];
    }
  }
  return out;
}

async function updateTaskStatus(taskId: number, newStatus: string) {
  // find current column + task
  const fromKey = findTaskColumn(taskId);
  const toKey = newStatus;
  if (!toKey) return;

  const existing =
    fromKey && project[fromKey]
      ? project[fromKey].find((t: any) => t.id === taskId)
      : null;

  // optimistic move
  if (fromKey && project[fromKey]) {
    project[fromKey] = project[fromKey].filter((t: any) => t.id !== taskId);
  }
  const optimistic = existing ? { ...existing, status: toKey } : { id: taskId, status: toKey };
  project[toKey] = [...(project[toKey] || []), optimistic];

  try {
    const res = await fetch(`/api/projects/${project.id}/tasks/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    const updated = await res.json();

    // patch only defined fields so we don't nuke title/desc/labels when backend omits them
    project[toKey] = project[toKey].map((t: any) =>
      t.id === taskId
        ? patchDefined(t, {
            title: updated.title,
            desc: updated.desc,
            status: updated.status,
            labels: updated.labels
          })
        : t
    );
  } catch (err: any) {
    // revert on failure
    project[toKey] = (project[toKey] || []).filter((t: any) => t.id !== taskId);
    if (fromKey) {
      project[fromKey] = [...(project[fromKey] || []), existing];
    }
    alert(err?.message ?? "Failed to update task");
  }
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

    const res = await fetch(`/api/projects/${project.id}`, {
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

    const payload = { desc: formData.get("note") };

    const res = await fetch(`/api/projects/${project.id}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const created = await res.json();
    project.notes = [...(project.notes || []), created];

    showAddNote = false;
    form.reset();
  }
  async function deleteNote(noteId: number) {
    const res = await fetch(
      `/api/projects/${project.id}/notes/${noteId}`,
      { method: "DELETE" }
    );

    if (res.ok) {
      project.notes = (project.notes || []).filter((n: any) => n.id !== noteId);
    }
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
    <button class="btn danger push-right" onclick={deleteProject}>Delete Project</button>
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
    {#each columns as col, colIdx}
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
                  {#each task.labels as label}
                    <span class="label">{label.name ?? label}</span>
                  {/each}
                </div>
              {/if}

              <!-- Card actions footer -->
              <div class="card-actions">
                <div class="left-actions">
                  {#if colIdx > 0}
                    <button class="btn small move-left" title="Move left" onclick={() => updateTaskStatus(task.id, columns[colIdx - 1].key)}>
                      <svg viewBox="0 0 24 24" class="icon_t"><path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                    </button>
                  {/if}
                </div>
                <div class="right-actions">
                  {#if colIdx < columns.length - 1}
                    <button class="btn small move-right" title="Move right" onclick={() => updateTaskStatus(task.id, columns[colIdx + 1].key)}>
                      <svg viewBox="0 0 24 24" class="icon_t"><path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                    </button>
                  {/if}
                  
                  <button class="btn small delete-task" title="Delete task" onclick={() => deleteTask(task.id)}>
                    <svg viewBox="0 0 24 24" class="icon_t"><path d="M6 7h12M10 11v6m4-6v6M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-12" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                  </button>
                </div>
              </div>
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
  {#if !loaded}
    <p>Loading…</p>
  {:else if loadError}
    <p>Project not found</p>
    <pre class="error">{loadError}</pre>
  {:else}
    <p>Project not found</p>
  {/if}
{/if}





